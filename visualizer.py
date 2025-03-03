try:
    import ffmpeg
    import numpy
    import matplotlib.pyplot as plt
    from PIL import Image
    from PIL import ImageDraw
except ImportError:
    print("Import error! Please install any missing libraries, then restart the script.")
    quit()
    
import math
import json
import tkinter; import tkinter.filedialog; import tkinter.ttk
import wave
import re
import os
import ctypes
import threading; from threading import Thread
import timeit
    
"""
yknow, when i was reading up on pysimplegui i didn't expect to have to pay 100 dollars

layout = [ 
    QLineEdit("Session export settings:")],
    QLineEdit("WAV file: ", key="audiofile"), gui.InputText(key="audiofile")],
    QLineEdit("Render filename: ", key="renderfile"), gui.InputText(key="renderfile")],
    QLineEdit("Render settings:")],
    QLineEdit("Video framerate:", key="framerate"), gui.InputText(key="framerate")],
    QLineEdit("Number of frequency bars to render:", key="bars"), gui.InputText(key="bars")],
    QLineEdit("Bar spacing (in pixels):", key="spacing"), gui.Input(key="spacing")],
    QLineEdit("Signal interpolation alpha:", key="lerp"), gui.InputText(key="lerp")],
    QLineEdit("Background image file:", key="background"), gui.InputText(key="background")],
    
    [gui.Button("Save Preset"), gui.Button("Load Preset")],
    [gui.Button("Continue")]
]
"""

directory = os.curdir
# Create window
root = tkinter.Tk()
root.title("Python-MV")
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('terriac.pythonmv')
root.iconbitmap("pymv.ico", "pymv.ico")

wave_name = tkinter.StringVar()
export_name = tkinter.StringVar()

defaultPreset = {
    "framerate": 30,
    "bars": 25,
    "bar_spacing": 5,
    "lerp_alpha": .75,
    "lerp_speed": 25
}

framerate = tkinter.StringVar(value=defaultPreset.get("framerate"))
bars = tkinter.StringVar(value=defaultPreset.get("bars"))
bar_spacing = tkinter.StringVar(value=defaultPreset.get("bar_spacing"))
lerp_alpha = tkinter.StringVar(value=defaultPreset.get("lerp_alpha"))
lerp_speed = tkinter.StringVar(value=defaultPreset.get("lerp_speed"))
background = tkinter.StringVar(value=defaultPreset.get("background"))

def toSignalScale(signal):
    if signal < 1:
        signal = 1
    return 20 * math.log10(signal)

# Typechecking callbacks
def check_num(newval):
    return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5
check_num_wrapper = (root.register(check_num), '%P')

def check_float(newval):
    return re.match('^[+-]?(?:[0-9]*[.])?[0-9]*$', newval) is not None and len(newval) <= 5
check_float_wrapper = (root.register(check_float), '%P')

# Dialog buttons
def save_preset():
    presetPath = tkinter.filedialog.asksaveasfilename(filetypes=[('JSON Preset', '*.json')], initialdir=directory+'/presets')
    presetPath = os.path.relpath(presetPath).replace("\\","/")
    
    with open(presetPath, 'w') as jsonOutput:
        json.dump({
            "framerate": int(framerate.get()),
            "bars": int(bars.get()),
            "bar_spacing": int(bar_spacing.get()),
            "lerp_alpha": float(lerp_alpha.get()),
            "lerp_speed": float(lerp_speed.get()),
            "background": background.get()
            }, jsonOutput)
def load_preset():
    presetPath = tkinter.filedialog.askopenfilename(filetypes=[('JSON Preset', '*.json')], initialdir=directory+'/presets')
    presetPath = os.path.relpath(presetPath).replace("\\","/")
    
    if not os.path.isfile(presetPath):
        tkinter.messagebox.showwarning("File not found", "Selected file does not exist.")
        return
    preset: dict = json.load(open(presetPath))
    
    framerate.set(preset.get("framerate", defaultPreset.get("framerate")))
    bars.set(preset.get("bars", defaultPreset.get("bars")))
    bar_spacing.set(preset.get("bar_spacing", defaultPreset.get("bar_spacing")))
    lerp_alpha.set(preset.get("lerp_alpha", defaultPreset.get("lerp_alpha")))
    lerp_speed.set(preset.get("lerp_speed", defaultPreset.get("lerp_speed")))
    background.set(preset.get("background", defaultPreset.get("background")))

elements = dict()
# Layout: [(Element, X, Y, Widthspan, Heightspan)]
layout = [
    (tkinter.Label(root, text="Import/Export:"), 0, 0, 2, 1),
    (tkinter.Label(root, text="Input file (.wav):"), 0, 1, 1, 1), (tkinter.Entry(root, textvariable=wave_name), 1, 1, 1, 1),
    (tkinter.Label(root, text="Export filename:"), 0, 2, 1, 1), (tkinter.Entry(root, textvariable=export_name), 1, 2, 1, 1),
    
    (tkinter.Label(root, text="Render settings:"), 2, 0, 2, 1),
    (tkinter.Label(root, text="Video framerate:"), 2, 1, 1, 1), (tkinter.Entry(root, textvariable=framerate, validate='key', validatecommand=check_num_wrapper), 3, 1, 1, 1),
    (tkinter.Label(root, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tkinter.Entry(root, textvariable=bars, validate='key', validatecommand=check_num_wrapper), 3, 2, 1, 1),
    (tkinter.Label(root, text="Bar spacing (px):"), 2, 3, 1, 1), (tkinter.Entry(root, textvariable=bar_spacing, validate='key', validatecommand=check_num_wrapper), 3, 3, 1, 1),
    (tkinter.Label(root, text="Inbetween interpolation alpha:"), 2, 4, 1, 1), (tkinter.Entry(root, textvariable=lerp_alpha, validate='key', validatecommand=check_float_wrapper), 3, 4, 1, 1),
    (tkinter.Label(root, text="Interpolation rate:"), 2, 5, 1, 1), (tkinter.Entry(root, textvariable=lerp_speed, validate='key', validatecommand=check_float_wrapper), 3, 5, 1, 1),
    (tkinter.Label(root, text="Background image file:"), 2, 6, 1, 1), (tkinter.Entry(root, textvariable=background), 3, 6, 1, 1),
    
    (tkinter.Button(root, text="Save Preset", command=save_preset), 0, 7, 1, 1),
    (tkinter.Button(root, text="Load Preset", command=load_preset), 1, 7, 1, 1)
]

for widget, c, r, cs, rs in layout:
    widget.grid(column=c, row=r, columnspan=cs, rowspan=rs, padx=5, pady=5)

progressLabel = tkinter.Label(root, text="Ready")
progressLabel.grid(column=1, row=8, columnspan=3, rowspan=3, padx=5, pady=5, sticky='w')
continueButton = tkinter.Button(root, text="Render")
continueButton.grid(column=3, row=7, columnspan=1, rowspan=1, padx=5, pady=5)
progressBar = tkinter.ttk.Progressbar(root, orient="horizontal", mode="determinate", maximum=1)
progressBar.grid(column=0, row=8, columnspan=1, rowspan=3, padx=5, pady=5)

interrupted = False
def interrupt():
    global interrupted
    interrupted = True

# Main functions
def render():
    fps = int(framerate.get())
    barCount = int(bars.get())
    barInterval = int(bar_spacing.get())
    lerp = float(lerp_alpha.get())
    lerpspeed = float(lerp_speed.get())
    inputFile = wave_name.get()

    wave_object = wave.open("files/" + inputFile)
        
    sample_rate = wave_object.getframerate()
    n_samples = wave_object.getnframes()
    t_audio = n_samples/sample_rate

    signal_wave = wave_object.readframes(n_samples)
    signal_array = numpy.frombuffer(signal_wave, dtype=numpy.int16)

    l_channel = signal_array[0::2]
    r_channel = signal_array[1::2]
    channel_average = abs(numpy.array(l_channel) + numpy.array(r_channel)) / 2
    spectogram = plt.specgram(channel_average, Fs=sample_rate, vmin=0, vmax=50)

    peak_signal = toSignalScale(numpy.max(channel_average))

    timeMult = sample_rate / fps

    freqMult = len(spectogram[1]) / 1.25 / barCount
    timeLen = len(spectogram[2])
    timeMult = timeLen / (n_samples / timeMult)

    frameCount = math.floor(timeLen/timeMult)

    print("File is %0.3f" %t_audio, "seconds long, render length: " + str(frameCount) + " frames.")

    cImage = Image.open('files/' + background.get()).convert("RGB")
    imageX, imageY = cImage.size

    video = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(imageX, imageY), r=fps)
    audio = ffmpeg.input('files/' + inputFile)

    process = (
        ffmpeg
        .concat(video, audio, v=1, a=1)
        .output('export/' + export_name.get(), pix_fmt='yuv420p', vcodec='libx264', r=fps)
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    
    renderStart = timeit.default_timer()

    prevSignals = [0] * barCount
    progressBar.configure(maximum = frameCount - 1)
    complete = threading.Event()
    global interrupted; interrupted = False
    def drawF(frameNo: int = 0):
        if interrupted or frameNo >= frameCount:
            complete.set()
            return
        
        frame = cImage.copy()  
        draw = ImageDraw.Draw(frame)

        for j in range(0, barCount):
            rawSignal = spectogram[0][round(j * freqMult)][round(frameNo * timeMult)]
            adjustedLerp = 1 - math.pow(1 - lerp, lerpspeed/fps)
            signal = toSignalScale(rawSignal) * adjustedLerp + prevSignals[j] * (1 - adjustedLerp)
            prevSignals[j] = signal
            size = abs(math.sqrt(signal / peak_signal) * imageY / 2)

            draw.rectangle((imageX / barCount * j + barInterval, imageY - size, imageX / barCount * (j + 1) - barInterval, imageY), fill = (255, 255, 255))

        process.stdin.write(
            numpy.array(frame).tobytes()
        )
        progressBar['value'] = frameNo + 1
        elapsed = timeit.default_timer() - renderStart
        progressLabel.configure(text=f"Rendering... {elapsed:.1f}s elapsed - {frameNo + 1}/{frameCount} - {frameNo/elapsed:.1f}/s - {frameNo/elapsed/fps:.3f}x render speed")
        root.after(1, lambda: drawF(frameNo + 1))
        
    
    continueButton.configure(text='Cancel', command=interrupt)
    
    root.after(1, drawF)

    complete.wait()
    process.stdin.close()
    process.wait()
    
    progressBar['value'] = 0
    continueButton.configure(text='Render', command=lambda: Thread(target=render).start())
    elapsed = timeit.default_timer() - renderStart
    progressLabel.configure(text=f"Finished in {elapsed:.1f}s - {frameCount}/{frameCount} - {frameCount/elapsed:.1f}/s - {frameCount/elapsed/fps:.3f}x render speed")

continueButton.configure(command=lambda: Thread(target=render).start())
root.mainloop()