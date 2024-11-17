import importlib
import os
import math
import random
import string
import json
import wave

try:
    import ffmpeg
    from matplotlib import image
    import numpy
    import matplotlib.pyplot as plt
    import PIL 
    from PIL import Image
    from PIL import ImageDraw
    from alive_progress import alive_bar
except ImportError:
    os.system('python -m pip install ffmpeg-python')
    os.system('python -m pip install numpy')
    os.system('python -m pip install pillow')
    os.system('python -m pip install matplotlib')
    os.system('python -m pip install alive-progress')
    print('Missing modules installed, please restart')
    quit()
    
def toSignalScale(signal):
    if signal < 1:
        signal = 1
    return 20 * math.log10(signal)

wave_name = input('WAV file: ')
export_name = input('Render filename: ')
wave_object = wave.open('files/' + wave_name)

settings = None

if input('Load preset? (Y/N): ') == 'Y':
    with open('presets/' + input('Preset name: ') + '.json') as preset:
        settings = json.load(preset)

if settings is None:
    videoFramerate = int(input('Video framerate: '))
    bars = int(input('Number of frequency bars to render: '))
    bar_spacing = int(input('Bar spacing (in pixels): '))
    lerp_alpha = float(input('Signal interpolation alpha: '))
    freq_exp = float(input('Frequency bar exponent: '))
    background = input('Background image file: ')
    if input('Save render settings as preset? (Y/N): ') == 'Y':
        with open('presets/' + input('Preset name: ') + '.json', 'w') as fp:
            json.dump({
                'framerate': videoFramerate,
                'bars': bars,
                'spacing': bar_spacing,
                'lerp': lerp_alpha,
                'background': background
                }, fp)
else:
    videoFramerate = settings['framerate']
    bars = settings['bars']
    bar_spacing = settings['spacing']
    lerp_alpha = settings['lerp']
    background = settings['background']
    
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

timeMult = sample_rate/videoFramerate
framerate = n_samples / timeMult

freqMult = len(spectogram[1]) / 1.25 / bars
timeLen = len(spectogram[2])
timeMult = timeLen/framerate

frameCount = math.floor(timeLen/timeMult)

print('File is %0.3f' %t_audio, 'seconds long, render length: ' + str(frameCount) + ' frames.')

cImage = Image.open('files/' + background).convert("RGB")
imageX, imageY = cImage.size

video = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(imageX, imageY), r=videoFramerate)
audio = ffmpeg.input('files/' + wave_name)

process = (
    ffmpeg
    .concat(video, audio, v=1, a=1)
    .output(export_name, pix_fmt='yuv420p', vcodec='libx264', r=videoFramerate)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

with alive_bar(frameCount) as bar:
    bar.text = 'Rendering frames...'
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
        bar()

process.stdin.close()
process.wait()