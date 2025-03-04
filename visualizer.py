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
    QLineEdit("Signal interpolation alpha:", key="_lerpAlpha"), gui.InputText(key="_lerpAlpha")],
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

inputFile = tkinter.StringVar()
export_name = tkinter.StringVar()

defaultPreset = {
    "framerate": 30,
    "bars": 25,
    "barSpacing": 5,
    "lerpAlpha": .75,
    "lerpSpeed": 25,
    "coverageX": 1,
    "coverageY": .5,
    "barJustifyX": .5,
    "barJustifyY": 1,
    "opacityExp": 0,
    "heightExp": .5
}

justifyHorizontal = [
"Left",
"Center",
"Right"
]
justifyVertical = [
"Top",
"Center",
"Bottom"
]

framerate = tkinter.StringVar(value=defaultPreset.get("framerate"))
bars = tkinter.StringVar(value=defaultPreset.get("bars"))
barSpacing = tkinter.StringVar(value=defaultPreset.get("barSpacing"))
lerpAlpha = tkinter.StringVar(value=defaultPreset.get("lerpAlpha"))
lerpSpeed = tkinter.StringVar(value=defaultPreset.get("lerpSpeed"))
background = tkinter.StringVar(value=defaultPreset.get("background"))

coverageX = tkinter.StringVar(value=defaultPreset.get("coverageX"))
coverageY = tkinter.StringVar(value=defaultPreset.get("coverageY"))
barJustifyX = tkinter.StringVar(value=defaultPreset.get("barJustifyX"))
barJustifyY = tkinter.StringVar(value=defaultPreset.get("barJustifyY"))
opacityExp = tkinter.StringVar(value=defaultPreset.get("opacityExp"))
heightExp = tkinter.StringVar(value=defaultPreset.get("heightExp"))

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
            "barSpacing": int(barSpacing.get()),
            "lerpAlpha": float(lerpAlpha.get()),
            "lerpSpeed": float(lerpSpeed.get()),
            "background": background.get(),
            
            "coverageX": float(coverageX.get()),
            "coverageY": float(coverageY.get()),
            "barJustifyX": float(barJustifyX.get()),
            "barJustifyY": float(barJustifyY.get()),
            "opacityExp": float(opacityExp.get()),
            "heightExp": float(heightExp.get())
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
    barSpacing.set(preset.get("barSpacing", defaultPreset.get("barSpacing")))
    lerpAlpha.set(preset.get("lerpAlpha", defaultPreset.get("lerpAlpha")))
    lerpSpeed.set(preset.get("lerpSpeed", defaultPreset.get("lerpSpeed")))
    background.set(preset.get("background", defaultPreset.get("background")))
    
    coverageX.set(preset.get("coverageX", defaultPreset.get("coverageX")))
    coverageY.set(preset.get("coverageY", defaultPreset.get("coverageY")))
    barJustifyX.set(preset.get("barJustifyX", defaultPreset.get("barJustifyX")))
    barJustifyY.set(preset.get("barJustifyY", defaultPreset.get("barJustifyY")))
    opacityExp.set(preset.get("opacityExp", defaultPreset.get("opacityExp")))
    heightExp.set(preset.get("heightExp", defaultPreset.get("heightExp")))

elements = dict()
# Layout: [(Element, X, Y, Widthspan, Heightspan)]
layout = [
    (tkinter.Label(root, text="Import/Export:"), 0, 0, 2, 1),
    (tkinter.Label(root, text="Input file (.wav):"), 0, 1, 1, 1), (tkinter.Entry(root, textvariable=inputFile), 1, 1, 1, 1),
    (tkinter.Label(root, text="Export filename:"), 0, 2, 1, 1), (tkinter.Entry(root, textvariable=export_name), 1, 2, 1, 1),
    
    (tkinter.Label(root, text="Render settings:"), 2, 0, 2, 1),
    (tkinter.Label(root, text="Video framerate:"), 2, 1, 1, 1), (tkinter.Entry(root, textvariable=framerate, validate='key', validatecommand=check_num_wrapper), 3, 1, 1, 1),
    (tkinter.Label(root, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tkinter.Entry(root, textvariable=bars, validate='key', validatecommand=check_num_wrapper), 3, 2, 1, 1),
    (tkinter.Label(root, text="Bar spacing (px):"), 2, 3, 1, 1), (tkinter.Entry(root, textvariable=barSpacing, validate='key', validatecommand=check_num_wrapper), 3, 3, 1, 1),
    (tkinter.Label(root, text="Inbetween interpolation alpha:"), 2, 4, 1, 1), (tkinter.Entry(root, textvariable=lerpAlpha, validate='key', validatecommand=check_float_wrapper), 3, 4, 1, 1),
    (tkinter.Label(root, text="Interpolation rate:"), 2, 5, 1, 1), (tkinter.Entry(root, textvariable=lerpSpeed, validate='key', validatecommand=check_float_wrapper), 3, 5, 1, 1),
    (tkinter.Label(root, text="Background image file:"), 2, 6, 1, 1), (tkinter.Entry(root, textvariable=background), 3, 6, 1, 1),
    
    (tkinter.Label(root, text="Bar customization:"), 4, 0, 2, 1),
    (tkinter.Label(root, text="Screen coverage width:"), 4, 1, 1, 1), (tkinter.Entry(root, textvariable=coverageX, validate='key', validatecommand=check_float_wrapper), 5, 1, 1, 1),
    (tkinter.Label(root, text="Screen coverage height:"), 4, 2, 1, 1), (tkinter.Entry(root, textvariable=coverageY, validate='key', validatecommand=check_float_wrapper), 5, 2, 1, 1),
    (tkinter.Label(root, text="Horizontal justification (left-right):"), 4, 3, 1, 1), (tkinter.Entry(root, textvariable=barJustifyX, validate='key', validatecommand=check_float_wrapper), 5, 3, 1, 1),
    (tkinter.Label(root, text="Vertical justification (top-bottom):"), 4, 4, 1, 1), (tkinter.Entry(root, textvariable=barJustifyY, validate='key', validatecommand=check_float_wrapper), 5, 4, 1, 1),
    (tkinter.Label(root, text="Opacity exponent:"), 4, 5, 1, 1), (tkinter.Entry(root, textvariable=opacityExp, validate='key', validatecommand=check_float_wrapper), 5, 5, 1, 1),
    (tkinter.Label(root, text="Height exponent:"), 4, 6, 1, 1), (tkinter.Entry(root, textvariable=heightExp, validate='key', validatecommand=check_float_wrapper), 5, 6, 1, 1),
    
    (tkinter.Button(root, text="Save Preset", command=save_preset), 0, 7, 1, 1),
    (tkinter.Button(root, text="Load Preset", command=load_preset), 1, 7, 1, 1)
]

for widget, c, r, cs, rs in layout:
    widget.grid(column=c, row=r, columnspan=cs, rowspan=rs, padx=5, pady=5)

progressLabel = tkinter.Label(root, text="Ready")
progressLabel.grid(column=1, row=8, columnspan=3, rowspan=3, padx=5, pady=5, sticky='w')
continueButton = tkinter.Button(root, text="Render")
continueButton.grid(column=2, row=7, columnspan=1, rowspan=1, padx=5, pady=5)
progressBar = tkinter.ttk.Progressbar(root, orient="horizontal", mode="determinate", maximum=1)
progressBar.grid(column=0, row=8, columnspan=1, rowspan=3, padx=5, pady=5)

# Main functions
def render():
    interrupted = False
    def interrupt():
        nonlocal interrupted; interrupted = "Render was cancelled."
    _framerate = int(framerate.get())
    _bars = int(bars.get())
    _barSpacing = int(barSpacing.get())
    _lerpAlpha = float(lerpAlpha.get())
    _lerpSpeed = float(lerpSpeed.get())
    _inputFile = inputFile.get()
    
    _coverageX = float(coverageX.get())
    _coverageY = float(coverageY.get())
    _barJustifyX = float(barJustifyX.get())
    _barJustifyY = float(barJustifyY.get())
    _opacityExp = float(opacityExp.get())
    _heightExp = float(heightExp.get())

    wave_object = wave.open("files/" + _inputFile)
        
    sample_rate = wave_object.getframerate()
    nSamples = wave_object.getnframes()
    tAudio = nSamples/sample_rate

    signalWave = wave_object.readframes(nSamples)
    signalArray = numpy.frombuffer(signalWave, dtype=numpy.int16)

    lChannel = signalArray[0::2]
    rChannel = signalArray[1::2]
    channelAverage = abs(numpy.array(lChannel) + numpy.array(rChannel)) / 2
    spectogram = plt.specgram(channelAverage, Fs=sample_rate, vmin=0, vmax=50)

    peak_signal = toSignalScale(numpy.max(channelAverage))

    frameInterval = sample_rate / _framerate

    freqMult = len(spectogram[1]) / 1.25 / _bars
    timeLen = len(spectogram[2])
    frameInterval = timeLen / (nSamples / frameInterval)

    frameCount = math.floor(timeLen/frameInterval)

    print("File is %0.3f" %tAudio, "seconds long, render length: " + str(frameCount) + " frames.")

    cImage = Image.open('files/' + background.get()).convert("RGB")
    imageWidth, imageHeight = cImage.size

    video = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(imageWidth, imageHeight), r=_framerate)
    audio = ffmpeg.input('files/' + _inputFile)

    process = (
        ffmpeg
        .concat(video, audio, v=1, a=1)
        .output('export/' + export_name.get(), pix_fmt='yuv420p', vcodec='libx264', r=_framerate)
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    
    renderStart = timeit.default_timer()

    prevSignals = [0] * _bars
    progressBar.configure(maximum = frameCount - 1)
    complete = threading.Event()
    widthGap = 1 - _coverageX
    def drawF(frameNo: int):
        if interrupted or frameNo >= frameCount:
            complete.set()
            return
        
        elapsed = timeit.default_timer() - renderStart
        progressLabel.configure(text=f"Rendering... {elapsed:.1f}s elapsed - {frameNo}/{frameCount} - {frameNo/elapsed:.1f}/s - {frameNo/elapsed/_framerate:.3f}x render speed")
        progressBar['value'] = frameNo
        
        frame = cImage.copy()  
        draw = ImageDraw.Draw(frame)

        for bar in range(0, _bars):
            rawSignal = spectogram[0][round(bar * freqMult)][round(frameNo * frameInterval)]
            adjustedLerp = 1 - math.pow(1 - _lerpAlpha, _lerpSpeed/_framerate)
            signal = toSignalScale(rawSignal) * adjustedLerp + prevSignals[bar] * (1 - adjustedLerp)
            prevSignals[bar] = signal
            signalFraction = signal / peak_signal
            
            width = _coverageX / _bars
            height = _coverageY * abs(math.pow(signalFraction, _heightExp))
            heightGap = 1 - height
            fillOpacity = int(255 * math.pow(signalFraction, _opacityExp))
            
            draw.rectangle(
                (
                    (widthGap * _barJustifyX + width * bar) * imageWidth + math.floor(_barSpacing / 2),
                    (heightGap * _barJustifyY) * imageHeight,
                    (widthGap * _barJustifyX + width * (bar + 1)) * imageWidth - math.ceil(_barSpacing / 2),
                    (heightGap * _barJustifyY + height) * imageHeight
                ), fill = (fillOpacity, fillOpacity, fillOpacity))

        process.stdin.write(
            numpy.array(frame).tobytes()
        )
    def drawWrapper(frameNo: int = 0):
        try:
            drawF(frameNo)
            root.after(1, lambda: drawWrapper(frameNo + 1))
        except Exception as error:
            nonlocal interrupted; interrupted = "A problem occured, please check output."
            print("Exception was caught:", error)
        
        
    
    continueButton.configure(text='Cancel', command=interrupt)
    
    root.after(1, drawWrapper)

    complete.wait()
    process.stdin.close()
    process.wait()
    
    progressBar['value'] = 0
    continueButton.configure(text='Render', command=lambda: Thread(target=render).start())
    totalElapsed = timeit.default_timer() - renderStart
    if interrupted:
        progressLabel.configure(text=interrupted)
    else:
        progressLabel.configure(text=f"Finished in {totalElapsed:.1f}s - {frameCount}/{frameCount} - {frameCount/totalElapsed:.1f}/s - {frameCount/totalElapsed/_framerate:.3f}x render speed")
    

continueButton.configure(command=lambda: Thread(target=render).start())
root.mainloop()