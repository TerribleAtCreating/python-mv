from import_modules import *
from resources import *
    
"""
yknow, when i was reading up on pysimplegui i didn't expect to have to pay 100 dollars

layout = [ 
    QLineedit("Session export settings:")],
    QLineedit("WAV file: ", key="audiofile"), gui.Inputtext(key="audiofile")],
    QLineedit("Render filename: ", key="renderfile"), gui.Inputtext(key="renderfile")],
    QLineedit("Render settings:")],
    QLineedit("Video framerate:", key="framerate"), gui.Inputtext(key="framerate")],
    QLineedit("Number of frequency bars to render:", key="bars"), gui.Inputtext(key="bars")],
    QLineedit("Bar spacing (in pixels):", key="spacing"), gui.Input(key="spacing")],
    QLineedit("Signal interpolation alpha:", key="_lerpalpha"), gui.Inputtext(key="_lerpalpha")],
    QLineedit("Background image file:", key="background"), gui.Inputtext(key="background")],
    
    [gui.Button("Save Preset"), gui.Button("Load Preset")],
    [gui.Button("Continue")]
]
"""

# Create window
root = tkinter.Tk()
root.title("Python-MV")
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('terriac.pythonmv')
root.iconbitmap("pymv.ico", "pymv.ico")

input_file = tkinter.StringVar()
export_file = tkinter.StringVar()
channel_pan = tkinter.StringVar()

defaultpreset = {
    "channel_pan": .5,
    "framerate": 30,
    "bars": 25,
    "bar_spacing": 5,
    "lerp_alpha": .75,
    "lerp_speed": 25,
    "coverage_x": 1,
    "coverage_y": .5,
    "bar_justify_x": .5,
    "bar_justify_y": 1,
    "brightness_exp": 0,
    "height_exp": .5
}

justify_horizontal = [
"Left",
"Center",
"Right"
]
justify_vertical = [
"Top",
"Center",
"Bottom"
]

channel_pan = tkinter.StringVar(value=defaultpreset.get("channel_pan"))

framerate = tkinter.StringVar(value=defaultpreset.get("framerate"))
bars = tkinter.StringVar(value=defaultpreset.get("bars"))
bar_spacing = tkinter.StringVar(value=defaultpreset.get("bar_spacing"))
lerp_alpha = tkinter.StringVar(value=defaultpreset.get("lerp_alpha"))
lerp_speed = tkinter.StringVar(value=defaultpreset.get("lerp_speed"))
background = tkinter.StringVar(value=defaultpreset.get("background"))

coverage_x = tkinter.StringVar(value=defaultpreset.get("coverage_x"))
coverage_y = tkinter.StringVar(value=defaultpreset.get("coverage_y"))
bar_justify_x = tkinter.StringVar(value=defaultpreset.get("bar_justify_x"))
bar_justify_y = tkinter.StringVar(value=defaultpreset.get("bar_justify_y"))
brightness_exp = tkinter.StringVar(value=defaultpreset.get("brightness_exp"))
height_exp = tkinter.StringVar(value=defaultpreset.get("height_exp"))

check_num_wrapper = (root.register(check_num), '%P')
check_float_wrapper = (root.register(check_float), '%P')

# Dialog buttons
def save_preset():
    presetpath = save_filename([('JSON Preset', '*.json')], '/presets')
    if not presetpath: return
    with open(presetpath, 'w') as jsonoutput:
        json.dump({
            "channelpan": float(channel_pan.get()),
            
            "framerate": int(framerate.get()),
            "bars": int(bars.get()),
            "bar_spacing": int(bar_spacing.get()),
            "lerp_alpha": float(lerp_alpha.get()),
            "lerp_speed": float(lerp_speed.get()),
            "background": background.get(),
            
            "coverage_x": float(coverage_x.get()),
            "coverage_y": float(coverage_y.get()),
            "bar_justify_x": float(bar_justify_x.get()),
            "bar_justify_y": float(bar_justify_y.get()),
            "brightness_exp": float(brightness_exp.get()),
            "height_exp": float(height_exp.get())
            }, jsonoutput)
def load_preset():
    presetpath = open_filename([('JSON Preset', '*.json')], '/presets')
    if not presetpath: return
    if not os.path.isfile(presetpath):
        tkinter.messagebox.showwarning("File not found", "Selected file does not exist.")
        return
    preset: dict = json.load(open(presetpath))
    
    channel_pan.set(preset.get("channel_pan", defaultpreset.get("channel_pan")))
    
    framerate.set(preset.get("framerate", defaultpreset.get("framerate")))
    bars.set(preset.get("bars", defaultpreset.get("bars")))
    bar_spacing.set(preset.get("bar_spacing", defaultpreset.get("bar_spacing")))
    lerp_alpha.set(preset.get("lerp_alpha", defaultpreset.get("lerp_alpha")))
    lerp_speed.set(preset.get("lerp_speed", defaultpreset.get("lerp_speed")))
    background.set(preset.get("background", defaultpreset.get("background")))
    
    coverage_x.set(preset.get("coverage_x", defaultpreset.get("coverage_x")))
    coverage_y.set(preset.get("coverage_y", defaultpreset.get("coverage_y")))
    bar_justify_x.set(preset.get("bar_justify_x", defaultpreset.get("bar_justify_x")))
    bar_justify_y.set(preset.get("bar_justify_y", defaultpreset.get("bar_justify_y")))
    brightness_exp.set(preset.get("brightness_exp", defaultpreset.get("brightness_exp")))
    height_exp.set(preset.get("height_exp", defaultpreset.get("height_exp")))

elements = dict()
# Layout: [(Element, X, Y, Widthspan, Heightspan)]
layout = {
    "import/export": [
        (tkinter.Label(root, text="Import/Export:"), 0, 0, 2, 1),
        (tkinter.Label(root, text="Input file (.wav):"), 0, 1, 1, 1), (OpenFileMenu(root, text="Select audio...", targetvariable=input_file, filetypes=[('Wave audio file', '*.wav')], initialdir='/files'), 1, 1, 1, 1),
        (tkinter.Label(root, text="Export filename:"), 0, 2, 1, 1), (SaveFileMenu(root, text="Select filename...", targetvariable=export_file, filetypes=[('MPEG-4 video file', '*.mp4')], initialdir='/export'), 1, 2, 1, 1),
        (tkinter.Label(root, text="Channel panning:"), 0, 3, 1, 1), (tkinter.Entry(root, textvariable=channel_pan, validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
    ],
    "render": [
        (tkinter.Label(root, text="Render settings:"), 2, 0, 2, 1),
        (tkinter.Label(root, text="Video framerate:"), 2, 1, 1, 1), (tkinter.Entry(root, textvariable=framerate, validate='key', validatecommand=check_num_wrapper), 3, 1, 1, 1),
        (tkinter.Label(root, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tkinter.Entry(root, textvariable=bars, validate='key', validatecommand=check_num_wrapper), 3, 2, 1, 1),
        (tkinter.Label(root, text="Bar spacing (px):"), 2, 3, 1, 1), (tkinter.Entry(root, textvariable=bar_spacing, validate='key', validatecommand=check_num_wrapper), 3, 3, 1, 1),
        (tkinter.Label(root, text="Inbetween interpolation alpha:"), 2, 4, 1, 1), (tkinter.Entry(root, textvariable=lerp_alpha, validate='key', validatecommand=check_float_wrapper), 3, 4, 1, 1),
        (tkinter.Label(root, text="Interpolation rate:"), 2, 5, 1, 1), (tkinter.Entry(root, textvariable=lerp_speed, validate='key', validatecommand=check_float_wrapper), 3, 5, 1, 1),
        (tkinter.Label(root, text="Background image file:"), 2, 6, 1, 1), (OpenFileMenu(root, text="Select background...", targetvariable=background, filetypes=[('PNG image file', '*.png')], initialdir='/files'), 3, 6, 1, 1),
    ],
    "bars": [
        (tkinter.Label(root, text="Bar customization:"), 4, 0, 2, 1),
        (tkinter.Label(root, text="Screen coverage width:"), 4, 1, 1, 1), (tkinter.Entry(root, textvariable=coverage_x, validate='key', validatecommand=check_float_wrapper), 5, 1, 1, 1),
        (tkinter.Label(root, text="Screen coverage height:"), 4, 2, 1, 1), (tkinter.Entry(root, textvariable=coverage_y, validate='key', validatecommand=check_float_wrapper), 5, 2, 1, 1),
        (tkinter.Label(root, text="Horizontal justification (left-right):"), 4, 3, 1, 1), (tkinter.Entry(root, textvariable=bar_justify_x, validate='key', validatecommand=check_float_wrapper), 5, 3, 1, 1),
        (tkinter.Label(root, text="Vertical justification (top-bottom):"), 4, 4, 1, 1), (tkinter.Entry(root, textvariable=bar_justify_y, validate='key', validatecommand=check_float_wrapper), 5, 4, 1, 1),
        (tkinter.Label(root, text="Brightness exponent:"), 4, 5, 1, 1), (tkinter.Entry(root, textvariable=brightness_exp, validate='key', validatecommand=check_float_wrapper), 5, 5, 1, 1),
        (tkinter.Label(root, text="Height exponent:"), 4, 6, 1, 1), (tkinter.Entry(root, textvariable=height_exp, validate='key', validatecommand=check_float_wrapper), 5, 6, 1, 1),
    ],
    "presets": [
        (tkinter.Button(root, text="Save Preset", command=save_preset), 0, 7, 1, 1),
        (tkinter.Button(root, text="Load Preset", command=load_preset), 1, 7, 1, 1)
    ]
}

for category in layout:
    for widget, c, r, cs, rs in category:
        sticky = None
        if isinstance(widget, tkinter.Label) and r > 0:
            sticky = 'e'
        if isinstance(widget, tkinter.Button) and r < 7:
            sticky = 'ew'
        widget.grid(sticky=sticky, column=c, row=r, columnspan=cs, rowspan=rs, padx=5, pady=5)

continue_button = tkinter.Button(root, text="Render")
continue_button.grid(column=2, row=7, columnspan=1, rowspan=1, padx=5, pady=5)

progress_bar = tkinter.ttk.progress_bar(root, orient="horizontal", mode="determinate", maximum=1)
progress_bar.grid(sticky='ew', column=0, row=8, columnspan=2, rowspan=3, padx=5, pady=5)
progress_label = tkinter.Label(root, text="Ready")
progress_label.grid(sticky='w', column=2, row=8, columnspan=3, rowspan=3, padx=5, pady=5)

# Main functions
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
        
        assert_empty(_input_file, "Input filename")
        assert_empty(_export_file, "Export filename")
        assert_empty(_background, "Background filename")
    except ValueError as error:
        interrupted = "Some provided render settings are invalid. Please double check that all render settings are filled, and check the output for details.\nif all settings were filled, please report this as an issue."
        tkinter.messagebox.showerror("Render settings invalidated", interrupted)
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

    print("File is %0.3f" %t_audio, "seconds long, render length: " + str(frame_count) + " frames.")

    cimage = Image.open('files/' + _background).convert("RGB")
    image_width, image_height = cimage.size

    video = ffmpeg.input('pipe:', format='rawvideo', pixfmt='rgb24', s='{}x{}'.format(image_width, image_height), r=_framerate)
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
        
        frame = cimage.copy()  
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
                    (width_gap * _bar_justify_x + width * bar) * image_width + math.floor(_bar_spacing / 2),
                    (height_gap * _bar_justify_y) * image_height,
                    (width_gap * _bar_justify_x + width * (bar + 1)) * image_width - math.ceil(_bar_spacing / 2),
                    (height_gap * _bar_justify_y + height) * image_height
                ), fill = (fill_brightness, fill_brightness, fill_brightness))

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
            tkinter.messagebox.showerror("Render interrupted", interrupted)
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
root.mainloop()