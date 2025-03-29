from import_modules import *
from resources import *
from ui import *

def render(preview=False):
    interrupted = False
    def interrupt():
        nonlocal interrupted; interrupted = "Render was cancelled."
    try:
        assert_empty(get_value('input_file'), "Input filename")
        assert_empty(get_value('export_file'), "Export filename")
        assert_empty(get_value('background'), "Background filename")
        if get_value('watermark_toggle'):
            assert_empty(get_value('watermark_file'), "Background filename")
            assert_enum(get_value('watermark_blending'), BlendingModes, "Watermark blending mode")
    except ValueError as error:
        interrupted = "Some provided render settings are invalid. Please double check that all render settings are filled, and check the output for details.\nif all settings were filled, please report this as an issue."
        print("Render settings invalidated:", error)
        tkinter.messagebox.showerror("Render settings invalidated", interrupted)
        return

    wave_object = wave.open("files/" + get_value('input_file'))
        
    sample_rate = wave_object.getframerate()
    n_samples = wave_object.getnframes()
    signal_wave = wave_object.readframes(n_samples)
    signal_array = numpy.frombuffer(signal_wave, dtype=numpy.int16)

    l_channel = signal_array[0::2]
    r_channel = signal_array[1::2]
    channel_average = abs(numpy.array(l_channel) * get_value('channel_pan') + numpy.array(r_channel) * (1 - get_value('channel_pan')))
    spectogram = plt.specgram(channel_average, Fs=sample_rate, vmin=0, vmax=50)
    peak_signal = preview and 1 or to_signal_scale(numpy.max(channel_average))

    freq_mult = len(spectogram[1]) / 1.25 / get_value('bars')
    time_length = len(spectogram[2])
    frame_interval = time_length / (n_samples / (sample_rate / get_value('framerate')))
    frame_count = math.floor(time_length/frame_interval)
    # frame_length = time_length / frame_count: will be used later for timeline based effects

    bg_image: Image.Image = Image.open('files/' + get_value('background')).convert('RGB')
    bg_image = ImageOps.scale(bg_image, max(min(*bg_image.size), ResolutionUpscale[get_value('video_upscale')]) / min(*bg_image.size))
    bg_image.resize((math.ceil(bg_image.size[0] / 2) * 2, math.ceil(bg_image.size[1] / 2) * 2))
    bg_width, bg_height = bg_image.size
    
    if get_value('watermark_toggle'):
        watermark_image: Image.Image = Image.open('files/' + get_value('watermark_file')).convert('RGB')
        watermark_adjust = min(bg_width / watermark_image.size[0], bg_height / watermark_image.size[1]) * get_value('watermark_size')
        
        watermark_image = ImageOps.scale(watermark_image, watermark_adjust)
        resized_watermark = Image.new('RGB', (bg_width, bg_height), (0, 0, 0))
        resized_watermark.paste(watermark_image, (int(bg_width / 2 - watermark_image.size[0] / 2), int(bg_height / 2 - watermark_image.size[1] / 2)))
    
    last_time = timeit.default_timer()
    elapsed = 0

    previous_signals = [0] * get_value('bars')
    progress_bar.configure(maximum = frame_count - 1)
    complete = threading.Event()
    thickness_gap = 1 - get_value('coverage_x')
    
    if get_value('watermark_toggle'): blender = BlendingModes[get_value('watermark_blending')]
    
    frame_average = 0
    time_average = 1
    
    def status_text(frame_no):
        frame_speed = frame_average / time_average
        render_speed = frame_speed/get_value('framerate')
        return (
        f"({elapsed:.1f}s), ETA: {(frame_count - frame_no) / get_value('framerate') / render_speed:.1f}s - "
        f"{frame_no}/{frame_count} - "
        f"{frame_speed:.1f}/s - " 
        f"{render_speed:.3f}x render speed"
        )
    
    def drawF(frame_no: int = 0):
        if interrupted or frame_no >= frame_count:
            return False
        
        frame = bg_image.copy()  
        draw = ImageDraw.Draw(frame)

        for bar in range(0, get_value('bars')):
            raw_signal = spectogram[0][round(bar * freq_mult)][round(frame_no * frame_interval)]
            adjusted_lerp = 1 - math.pow(1 - get_value('lerp_alpha'), get_value('lerp_speed')/get_value('framerate'))
            signal = to_signal_scale(raw_signal) * adjusted_lerp + previous_signals[bar] * (1 - adjusted_lerp)
            previous_signals[bar] = signal
            
            # Use an if statement, since 0 will be interpreted as False and move to the actual value instead
            if preview:
                signal_fraction = bar / (get_value('bars') - 1)
            else:
                signal_fraction = signal / peak_signal
            
            bar_thickness = get_value('coverage_x') / get_value('bars')
            bar_length = get_value('coverage_y') * abs(math.pow(signal_fraction, get_value('height_exp')))
            length_gap = 1 - bar_length
            fill_brightness = int(255 * math.pow(signal_fraction, get_value('brightness_exp')))
            
            spacing_half = get_value('bar_spacing') / 2
            spacing_min, spacing_max = math.floor(spacing_half), math.ceil(spacing_half)
            fill_color = (fill_brightness, fill_brightness, fill_brightness)
            if get_value("bar_orientation"):
                # Vertical orientation
                bar_coordinates = [
                    (length_gap * get_value('bar_justify_x')) * bg_width,
                    (thickness_gap * get_value('bar_justify_y') + bar_thickness * bar) * bg_height + spacing_min,
                    (length_gap * get_value('bar_justify_x') + bar_length) * bg_width
                    (thickness_gap * get_value('bar_justify_y') + bar_thickness * (bar + 1)) * bg_height - spacing_max
                ]
            else:
                # Horizontal orientation
                bar_coordinates = [
                    (thickness_gap * get_value('bar_justify_x') + bar_thickness * bar) * bg_width + spacing_min,
                    (length_gap * get_value('bar_justify_y')) * bg_height,
                    (thickness_gap * get_value('bar_justify_x') + bar_thickness * (bar + 1)) * bg_width - spacing_max,
                    (length_gap * get_value('bar_justify_y') + bar_length) * bg_height
                ]
            draw.rectangle(*bar_coordinates, fill = fill_color)
        
        if get_value('watermark_toggle'): frame = blender(frame, resized_watermark)
        return frame

    export_path = 'export/' + get_value('export_file')
    if preview:
        preview_path = 'export/preview.png'
        drawF().save(preview_path)
        os.startfile(os.path.abspath(preview_path))
            
        return
    else:
        video = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(bg_width, bg_height), r=get_value('framerate'))
        audio = ffmpeg.input('files/' + get_value('input_file'))
        process = (
            ffmpeg
            .concat(video, audio, v=1, a=1)
            .output(export_path, pix_fmt='yuv420p', vcodec='libx264', r=get_value('framerate'))
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
    def drawwrapper(frame_no: int = 0):
        try:
            frame = drawF(frame_no)
            
            nonlocal last_time; nonlocal elapsed
            delta_time = timeit.default_timer() - last_time
            elapsed += delta_time
            last_time += delta_time
            
            # Calculate render speed
            nonlocal frame_average; nonlocal time_average
            frame_average += 1
            time_average += delta_time
            
            frame_average /= time_average
            time_average = 1
            
            if not preview:
                progress_label.configure(text="Rendering... " + status_text(frame_no + 1))
                progress_bar['value'] = frame_no
            
            if frame:
                process.stdin.write(numpy.array(frame).tobytes())
                root.after(1, lambda: drawwrapper(frame_no + 1))
            else:
                complete.set()
        except Exception as error:
            nonlocal interrupted; interrupted = "A problem occured, please check the output for errors."
            tkinter.messagebox.showerror("Render interrupted", interrupted)
            traceback.print_exc()
            
            complete.set()
    
    continue_button.configure(text='Cancel', command=interrupt)
    set_ui_state('disabled')
    
    root.after(1, drawwrapper)

    complete.wait()
    process.stdin.close()
    process.wait()
    
    progress_bar['value'] = 0
    continue_button.configure(text='Render', command=lambda: Thread(target=render).start())
    set_ui_state('normal')
    if interrupted:
        progress_label.configure(text=interrupted)
    else:
        progress_label.configure(text="Finished " + status_text(frame_count))
        os.startfile(os.path.abspath(export_path))
        
continue_button.configure(command=lambda: Thread(target=render).start())
preview_button.configure(command=lambda: Thread(target=render, args=[True]).start())
launch_ui()