from import_modules import *
from resources import *
from ui import *

def render():
    interrupted = False
    def interrupt():
        nonlocal interrupted; interrupted = "Render was cancelled."
    try:
        _input_file = input_file.get()
        _export_file = export_file.get()
        _channel_pan = float(channel_pan.get())
            
        _framerate = int(framerate.get())
        _bars = int(bars.get())
        _bar_spacing = int(bar_spacing.get())
        _lerp_alpha = float(lerp_alpha.get())
        _lerp_speed = float(lerp_speed.get())
        _background = background.get()
        
        _coverage_x = float(coverage_x.get())
        _coverage_y = float(coverage_y.get())
        _bar_justify_x = float(bar_justify_x.get())
        _bar_justify_y = float(bar_justify_y.get())
        _brightness_exp = float(brightness_exp.get())
        _height_exp = float(height_exp.get())
        
        _watermark_toggle = watermark_toggle.get()
        _watermark_file = watermark_file.get()
        
        assert_empty(_input_file, "Input filename")
        assert_empty(_export_file, "Export filename")
        assert_empty(_background, "Background filename")
    except ValueError as error:
        interrupted = "Some provided render settings are invalid. Please double check that all render settings are filled, and check the output for details.\nif all settings were filled, please report this as an issue."
        ttk.messagebox.showerror("Render settings invalidated", interrupted)
        print("Render settings invalidated:", error)
        return

    wave_object = wave.open("files/" + _input_file)
        
    sample_rate = wave_object.getframerate()
    n_samples = wave_object.getnframes()
    t_audio = n_samples/sample_rate
    signal_wave = wave_object.readframes(n_samples)
    signal_array = numpy.frombuffer(signal_wave, dtype=numpy.int16)

    l_channel = signal_array[0::2]
    r_channel = signal_array[1::2]
    channel_average = abs(numpy.array(l_channel) * _channel_pan + numpy.array(r_channel) * (1 - _channel_pan))
    spectogram = plt.specgram(channel_average, Fs=sample_rate, vmin=0, vmax=50)
    peak_signal = to_signal_scale(numpy.max(channel_average))

    freq_mult = len(spectogram[1]) / 1.25 / _bars
    time_length = len(spectogram[2])
    frame_interval = time_length / (n_samples / (sample_rate / _framerate))
    frame_count = math.floor(time_length/frame_interval)
    frame_length = time_length / frame_count

    print("File is %0.3f" %t_audio, "seconds long, render length: " + str(frame_count) + " frames.")
    bg_image: Image.Image = Image.open('files/' + _background).convert("RGB")
    
    watermark_image: Image.Image = Image.open('files/' + _watermark_file).convert("RGB")
    bg_width, bg_height = bg_image.size
    watermark_width, watermark_height = watermark_image.size
    watermark_size = math.max(watermark_width / bg_width, watermark_height / bg_height)
    watermark_image = ImageOps.fit(watermark_image, ((watermark_width / watermark_size), (watermark_height / watermark_size)))

    video = ffmpeg.input('pipe:', format='rawvideo', pixfmt='rgb24', s='{}x{}'.format(bg_width, bg_height), r=_framerate)
    audio = ffmpeg.input('files/' + _input_file)

    process = (
        ffmpeg
        .concat(video, audio, v=1, a=1)
        .output('export/' + _export_file, pixfmt='yuv420p', vcodec='libx264', r=_framerate)
        .overwriteoutput()
        .runasync(pipestdin=True)
    )
    
    render_start = timeit.defaulttimer()

    previous_signals = [0] * _bars
    progress_bar.configure(maximum = frame_count - 1)
    complete = threading.Event()
    width_gap = 1 - _coverage_x
    def drawF(frameno: int):
        if interrupted or frameno >= frame_count:
            return False
        
        elapsed = timeit.defaulttimer() - render_start
        progress_label.configure(text=f"Rendering... {elapsed:.1f}s elapsed - {frameno}/{frame_count} - {frameno/elapsed:.1f}/s - {frameno/elapsed/_framerate:.3f}x render speed")
        progress_bar['value'] = frameno
        
        frame = bg_image.copy()  
        draw = ImageDraw.Draw(frame)

        for bar in range(0, _bars):
            raw_signal = spectogram[0][round(bar * freq_mult)][round(frameno * frame_interval)]
            adjusted_lerp = 1 - math.pow(1 - _lerp_alpha, _lerp_speed/_framerate)
            signal = to_signal_scale(raw_signal) * adjusted_lerp + previous_signals[bar] * (1 - adjusted_lerp)
            previous_signals[bar] = signal
            signal_fraction = signal / peak_signal
            
            width = _coverage_x / _bars
            height = _coverage_y * abs(math.pow(signal_fraction, _height_exp))
            height_gap = 1 - height
            fill_brightness = int(255 * math.pow(signal_fraction, _brightness_exp))
            
            draw.rectangle(
                (
                    (width_gap * _bar_justify_x + width * bar) * bg_width + math.floor(_bar_spacing / 2),
                    (height_gap * _bar_justify_y) * bg_height,
                    (width_gap * _bar_justify_x + width * (bar + 1)) * bg_width - math.ceil(_bar_spacing / 2),
                    (height_gap * _bar_justify_y + height) * bg_height
                ), fill = (fill_brightness, fill_brightness, fill_brightness))
        
        frame = ImageChops.add(frame, watermark_image)
        
        process.stdin.write(
            numpy.array(frame).tobytes()
        )
        
        return True
    def drawwrapper(frameno: int = 0):
        try:
            if drawF(frameno):
                root.after(1, lambda: drawwrapper(frameno + 1))
            else:
                complete.set()
        except Exception as error:
            nonlocal interrupted; interrupted = "A problem occured, please check the output for errors."
            ttk.messagebox.showerror("Render interrupted", interrupted)
            print("Exception was caught:", error)
    
    continue_button.configure(text='Cancel', command=interrupt)
    
    root.after(1, drawwrapper)

    complete.wait()
    process.stdin.close()
    process.wait()
    
    progress_bar['value'] = 0
    continue_button.configure(text='Render', command=lambda: Thread(target=render).start())
    total_elapsed = timeit.defaulttimer() - render_start
    if interrupted:
        progress_label.configure(text=interrupted)
    else:
        progress_label.configure(text=f"Finished in {total_elapsed:.1f}s - {frame_count}/{frame_count} - {frame_count/total_elapsed:.1f}/s - {frame_count/total_elapsed/_framerate:.3f}x render speed")
        
continue_button.configure(command=lambda: Thread(target=render).start())
launch_ui()