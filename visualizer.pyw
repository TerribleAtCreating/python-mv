import sys
import math
import json
import wave

try:
    import ffmpeg
    import tkinter as tk
    import numpy
    import matplotlib.pyplot as plt
    import PIL
    from PIL import Image
    from PIL import ImageDraw
    from alive_progress import alive_bar
except ImportError:
    print("Import error! Please install any missing libraries, then restart the script.")
    quit()
    
def toSignalScale(signal):
    if signal < 1:
        signal = 1
    return 20 * math.log10(signal)

# Typechecking callbacks
def isDigitLetter(v):
    if str.isdigit(v) or v == "":
        return True
    else:
        return False
    
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

# Create window
root = tk.Tk()
root.title("Python-MV")
root.minsize(400, 225)
root.maxsize(2000, 1125)

width, height = 1600, 900
x = int((root.winfo_screenwidth()/2) - (width/2))
y = int((root.winfo_screenheight()/2) - (height/1.5))
root.geometry(f"{width}x{height}+{x}+{y}")  # width x height + x + y

wave_name = tk.StringVar()
export_name = tk.StringVar()

video_framerate = tk.StringVar()
bars = tk.StringVar()
bar_spacing = tk.StringVar()
lerp_alpha = tk.StringVar()
background = tk.StringVar()

press = tk.BooleanVar(False)

elements = dict()
layout = [
    (tk.Label(root, text="Import/Export:"), 0, 0, 2, 1),
    (tk.Label(root, text="Input file (.wav):"), 0, 1, 1, 1), (tk.Entry(root, textvariable=wave_name), 1, 1, 1, 1),
    (tk.Label(root, text="Export filename:"), 0, 2, 1, 1), (tk.Entry(root, textvariable=export_name), 1, 2, 1, 1),
    
    (tk.Label(root, text="Render settings:"), 2, 0, 2, 1),
    (tk.Label(root, text="Video framerate:"), 2, 1, 1, 1), (tk.Entry(root, textvariable=video_framerate), 3, 1, 1, 1),
    (tk.Label(root, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tk.Entry(root, textvariable=bars), 3, 2, 1, 1),
    (tk.Label(root, text="Bar spacing (px):"), 2, 3, 1, 1), (tk.Entry(root, textvariable=bar_spacing), 3, 3, 1, 1),
    (tk.Label(root, text="Signal interpolation alpha:"), 2, 4, 1, 1), (tk.Entry(root, textvariable=lerp_alpha), 3, 4, 1, 1),
    (tk.Label(root, text="Background image file:"), 2, 5, 1, 1), (tk.Entry(root, textvariable=background), 3, 5, 1, 1),
    
    (tk.Button(root, text="Save Preset"), 0, 6, 1, 1),
    (tk.Button(root, text="Load Preset"), 1, 6, 1, 1),
    (tk.Button(root, text="Continue", command=lambda: press.set(True)), 3, 6, 1, 1, "start")
]

for widget, c, r, cs, rs, name in layout:
    widget.grid(column=c, row=r, columnspan=cs, rowspan=rs, padx=5, pady=5)
    if not name is None:
        elements[name] = widget

root.mainloop()   
elements["start"].wait_variable(press)
root.quit()
    
wave_name = wave_name.get()
export_name = export_name.get()

video_framerate = int(video_framerate.get())
bars = int(bars.get())
bar_spacing = int(bar_spacing.get())
lerp_alpha = float(lerp_alpha.get())
background = background.get()

wave_object = wave.open("files/" + wave_name.get())

settings = None
    
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

timeMult = sample_rate/int(video_framerate.get())
framerate = n_samples / timeMult

freqMult = len(spectogram[1]) / 1.25 / bars
timeLen = len(spectogram[2])
timeMult = timeLen/framerate

frameCount = math.floor(timeLen/timeMult)

print("File is %0.3f" %t_audio, "seconds long, render length: " + str(frameCount) + " frames.")

cImage = Image.open("files/" + background).convert("RGB")
imageX, imageY = cImage.size

video = ffmpeg.input("pipe:", format="rawvideo", pix_fmt="rgb24", s="{}x{}".format(imageX, imageY), r=video_framerate)
audio = ffmpeg.input("files/" + wave_name)

process = (
    ffmpeg
    .concat(video, audio, v=1, a=1)
    .output(export_name.get(), pix_fmt="yuv420p", vcodec="libx264", r=video_framerate)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

prevSignals = [0] * bars
for i in range(0, math.floor(frameCount)):
    frame = cImage.copy()  
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, cImage.size[1] - 10, cImage.size[0], cImage.size[1] - 10), (255, 255, 255))

    for j in range(0, bars):
        rawSignal = spectogram[0][round(j * freqMult)][round(i * timeMult)]
        signal = toSignalScale(rawSignal) * lerp_alpha + prevSignals[j] * (1 - lerp_alpha)
        prevSignals[j] = signal
        size = abs(math.sqrt(signal / peak_signal) * imageY / 2)

        draw.rectangle((imageX / bars * j + bar_spacing, imageY - size, imageX / bars * (j + 1) - bar_spacing, imageY), fill = (255, 255, 255))

    process.stdin.write(
        numpy.array(frame).tobytes()
    )

process.stdin.close()
process.wait()