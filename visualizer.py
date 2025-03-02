try:
    import ffmpeg
    import numpy
    import matplotlib.pyplot as plt
    import PIL
    from PIL import Image
    from PIL import ImageDraw
    from alive_progress import alive_bar
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

framerate = tkinter.StringVar(value=60)
bars = tkinter.StringVar(value=25)
bar_spacing = tkinter.StringVar(value=5)
lerp_alpha = tkinter.StringVar(value=.75)
lerp_speed = tkinter.StringVar(value=25)
background = tkinter.StringVar(value="greenscreen.png")

def toSignalScale(signal):
    if signal < 1:
        signal = 1
    return 20 * math.log10(signal)

# Typechecking callbacks
def check_num(newval):
    return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5
check_num_wrapper = (root.register(check_num), '%P')

def check_float(newval):
    return re.match('[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)', newval) is not None and len(newval) <= 5
check_float_wrapper = (root.register(check_num), '%P')

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
            "background": background.get()
            }, jsonOutput)
def load_preset():
    presetPath = tkinter.filedialog.askopenfilename(filetypes=[('JSON Preset', '*.json')], initialdir=directory+'/presets')
    presetPath = os.path.relpath(presetPath).replace("\\","/")
    
    if not os.path.isfile(presetPath):
        tkinter.messagebox.showwarning("File not found", "Selected file does not exist.")
        return
    preset = json.load(open(presetPath))
    
    framerate.set(preset["framerate"])
    bars.set(preset["bars"])
    bar_spacing.set(preset["bar_spacing"])
    lerp_alpha.set(preset["lerp_alpha"])
    background.set(preset["background"])

elements = dict()
# Layout: [(Element, X, Y, Widthspan, Heightspan)]
layout = [
    (tkinter.Label(root, text="Import/Export:"), 0, 0, 2, 1),
    (tkinter.Label(root, text="Input file (.wav):"), 0, 1, 1, 1), (tkinter.Entry(root, textvariable=wave_name), 1, 1, 1, 1),
    (tkinter.Label(root, text="Export filename:"), 0, 2, 1, 1), (tkinter.Entry(root, textvariable=export_name), 1, 2, 1, 1),
    
    (tkinter.Label(root, text="Render settings:"), 2, 0, 2, 1),
    (tkinter.Label(root, text="Video framerate:"), 2, 1, 1, 1), (tkinter.Entry(root, textvariable=framerate, validatecommand=check_num_wrapper), 3, 1, 1, 1),
    (tkinter.Label(root, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tkinter.Entry(root, textvariable=bars, validatecommand=check_num_wrapper), 3, 2, 1, 1),
    (tkinter.Label(root, text="Bar spacing (px):"), 2, 3, 1, 1), (tkinter.Entry(root, textvariable=bar_spacing, validatecommand=check_num_wrapper), 3, 3, 1, 1),
    (tkinter.Label(root, text="Inbetween interpolation alpha:"), 2, 4, 1, 1), (tkinter.Entry(root, textvariable=lerp_alpha, validatecommand=check_float_wrapper), 3, 4, 1, 1),
    (tkinter.Label(root, text="Interpolation rate:"), 2, 5, 1, 1), (tkinter.Entry(root, textvariable=lerp_speed, validatecommand=check_float_wrapper), 3, 5, 1, 1),
    (tkinter.Label(root, text="Background image file:"), 2, 6, 1, 1), (tkinter.Entry(root, textvariable=background), 3, 6, 1, 1),
    
    (tkinter.Button(root, text="Save Preset", command=save_preset), 0, 7, 1, 1),
    (tkinter.Button(root, text="Load Preset", command=load_preset), 1, 7, 1, 1)
]

for widget, c, r, cs, rs in layout:
    widget.grid(column=c, row=r, columnspan=cs, rowspan=rs, padx=5, pady=5)

continue_button = tkinter.Button(root, text="Continue")
continue_button.grid(column=3, row=7, columnspan=1, rowspan=1, padx=5, pady=5)
progressBar = tkinter.ttk.Progressbar(root, orient="horizontal", mode="determinate", maximum=1)
progressBar.grid(column=0, row=8, columnspan=1, rowspan=3, padx=5, pady=5)

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

    prevSignals = [0] * barCount
    interrupted = False
    progressBar.configure(maximum = frameCount - 1)
    def interrupt():
        interrupted = True
    with alive_bar(math.floor(frameCount)) as bar:
        def draw(frameNo: int):
            bar()
            progressBar['value'] = frameNo + 1
            
            frame = cImage.copy()  
            draw = ImageDraw.Draw(frame)
            # draw.rectangle((0, cImage.size[1] - 10, cImage.size[0], cImage.size[1] - 10), (255, 255, 255))

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
            
        
        continue_button.configure(text='Cancel', command=interrupt)
        root.after(1)
        for i in range(0, math.floor(frameCount)):
            if interrupted:
                break
            draw(i)
            root.after(1)

    process.stdin.close()
    process.wait()
    
    progressBar['value'] = 0
    continue_button.configure(text='Continue', command=render)

continue_button.configure(command=render)
root.mainloop()