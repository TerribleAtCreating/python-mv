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
        tkinter.messagebox.showerror("Render settings invalidated", interrupted)
        print("Render settings invalidated:", error)
        return

    wave_object = wave.open("files/" + get_value('input_file'))
        
    sample_rate = wave_object.getframerate()
    n_samples = wave_object.getnframes()
    signal_wave = wave_object.readframes(n_samples)
    signal_array = numpy.frombuffer(signal_wave, dtype=numpy.int16)

    l_channel = signal_array[0::2]
    r_channel = signal_array[1::2]
    channel_average = abs(numpy.array(l_channel) * float(get_value('channel_pan')) + numpy.array(r_channel) * (1 - float(get_value('channel_pan'))))
    spectogram = plt.specgram(channel_average, Fs=sample_rate, vmin=0, vmax=50)
    peak_signal = preview and 1 or to_signal_scale(numpy.max(channel_average))

    freq_mult = len(spectogram[1]) / 1.25 / int(get_value('bars'))
    time_length = len(spectogram[2])
    frame_interval = time_length / (n_samples / (sample_rate / int(get_value('framerate'))))
    frame_count = math.floor(time_length/frame_interval)
    # frame_length = time_length / frame_count: will be used later for timeline based effects

    bg_image: Image.Image = Image.open('files/' + get_value('background')).convert('RGB')
    
    bg_width, bg_height = bg_image.size
    
    if get_value('watermark_toggle'):
        watermark_image: Image.Image = Image.open('files/' + get_value('watermark_file')).convert('RGB')
        watermark_width, watermark_height = watermark_image.size
        watermark_adjust = 1 / max(watermark_width / bg_width, watermark_height / bg_height) * float(get_value('watermark_size'))
        resized_watermark = Image.new('RGB', (bg_width, bg_height), (0, 0, 0))
        resized_watermark.paste(ImageOps.scale(watermark_image, watermark_adjust), (int(bg_width / 2 - watermark_width / 2), int(bg_height / 2 - watermark_height / 2)))
    
    render_start = timeit.default_timer()

    previous_signals = [0] * int(get_value('bars'))
    progress_bar.configure(maximum = frame_count - 1)
    complete = threading.Event()
    width_gap = 1 - float(get_value('coverage_x'))
    
    blender = BlendingModes[get_value('watermark_blending')]
    def drawF(frame_no: int = 0):
        if interrupted or frame_no >= frame_count:
            return False
        
        elapsed = timeit.default_timer() - render_start
        if not preview:
            progress_label.configure(text=f"Rendering... {elapsed:.1f}s elapsed - {frame_no}/{frame_count} - {frame_no/elapsed:.1f}/s - {frame_no/elapsed/get_value('framerate'):.3f}x render speed")
            progress_bar['value'] = frame_no
        
        frame = bg_image.copy()  
        draw = ImageDraw.Draw(frame)

        for bar in range(0, int(get_value('bars'))):
            raw_signal = spectogram[0][round(bar * freq_mult)][round(frame_no * frame_interval)]
            adjusted_lerp = 1 - math.pow(1 - float(get_value('lerp_alpha')), float(get_value('lerp_speed'))/get_value('framerate'))
            signal = to_signal_scale(raw_signal) * adjusted_lerp + previous_signals[bar] * (1 - adjusted_lerp)
            previous_signals[bar] = signal
            signal_fraction = preview and bar / (int(get_value('bars')) - 1) or signal / peak_signal
            
            width = float(get_value('coverage_x')) / int(get_value('bars'))
            height = float(get_value('coverage_y')) * abs(math.pow(signal_fraction, float(get_value('height_exp'))))
            height_gap = 1 - height
            fill_brightness = int(255 * math.pow(signal_fraction, float(get_value('brightness_exp'))))
            
            draw.rectangle(
                (
                    (width_gap * float(get_value('bar_justify_x')) + width * bar) * bg_width + math.floor(int(get_value('bar_spacing')) / 2),
                    (height_gap * float(get_value('bar_justify_y'))) * bg_height,
                    (width_gap * float(get_value('bar_justify_x')) + width * (bar + 1)) * bg_width - math.ceil(int(get_value('bar_spacing')) / 2),
                    (height_gap * float(get_value('bar_justify_y')) + height) * bg_height
                ), fill = (fill_brightness, fill_brightness, fill_brightness))
        
        if get_value('watermark_toggle'): frame = blender(frame, resized_watermark)
        return frame

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
            .output('export/' + get_value('export_file'), pix_fmt='yuv420p', vcodec='libx264', r=get_value('framerate'))
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
    def drawwrapper(frame_no: int = 0):
        try:
            frame = drawF(frame_no)
            if drawF(frame_no):
                process.stdin.write(numpy.array(frame).tobytes())
                root.after(1, lambda: drawwrapper(frame_no + 1))
            else:
                complete.set()
        except Exception as error:
            nonlocal interrupted; interrupted = "A problem occured, please check the output for errors."
            tkinter.messagebox.showerror("Render interrupted", interrupted)
            print("Exception was caught:", error)
    
    continue_button.configure(text='Cancel', command=interrupt)
    set_ui_state('disabled')
    
    root.after(1, drawwrapper)

    complete.wait()
    process.stdin.close()
    process.wait()
    
    progress_bar['value'] = 0
    continue_button.configure(text='Render', command=lambda: Thread(target=render).start())
    set_ui_state('normal')
    total_elapsed = timeit.default_timer() - render_start
    if interrupted:
        progress_label.configure(text=interrupted)
    else:
        progress_label.configure(text=f"Finished in {total_elapsed:.1f}s - {frame_count}/{frame_count} - {frame_count/total_elapsed:.1f}/s - {frame_count/total_elapsed/int(get_value('framerate')):.3f}x render speed")
        
continue_button.configure(command=lambda: Thread(target=render).start())
preview_button.configure(command=lambda: Thread(target=render, args=[True]).start())
launch_ui()