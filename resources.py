from import_modules import *

AUDIO_EXTS = ('.wav', '.mp3', '.flac', '.m4a', '.aac', '.ogg', '.oga', '.opus', '.wma', '.aiff', '.aif', '.ape', '.amr', '.mid', '.midi')

class DialogFiletypes:
    png    = ('PNG image file', '*.png')
    jpg    = ('JPEG image file', '*.jpg;*.jpeg')
    gif    = ('GIF image file', '*.gif')
    json   = ('JSON preset', '*.json')
    jsonPreset = ('JSON preset', '*.json')
    wav    = ('Wave audio file', '*.wav')
    mp3    = ('MPEG-3 audio file', '*.mp3')
    audio  = ('Audio file', '*.wav;*.mp3;*.flac;*.m4a;*.aac;*.ogg;*.oga;*.opus;*.wma;*.aiff;*.aif;*.ape;*.amr;*.mid;*.midi')
    mp4    = ('MPEG-4 video file', '*.mp4')
    webm   = ('WebM video file', '*.webm')
    video  = ('Video file', '*.mp4;*.webm;*.gif;*.mov')

BlendingModes = {
    "Additive": ImageChops.add,
    "Additive Modulo": ImageChops.add_modulo,
    "Subtractive": ImageChops.subtract,
    "Subtractive Modulo": ImageChops.subtract_modulo,
    "Difference": ImageChops.difference,
}

ResolutionUpscale = {
    "No upscale": 0,
    "720p (SD)": 720,
    "1080p (HD)": 1080,
    "1440p (QHD)": 1440,
    "2160p (UHD - 4K)": 2160,
    "4320p (UHD - 8K)": 4320
}

OutputFormats = {
    "MP4":           {"ext": ".mp4",  "encoders": ["Auto", "libx264 (CPU)", "h264_nvenc (NVIDIA GPU)", "libx265 (HEVC, CPU)", "hevc_nvenc (NVIDIA GPU)"]},
    "WebM":          {"ext": ".webm", "encoders": ["Auto", "libvpx-vp9 (CPU)"]},
    "GIF":           {"ext": ".gif",  "encoders": ["Auto"]},
    "PNG sequence":  {"ext": "",      "encoders": ["None"]}
}

Encoders = {
    "Auto": None,
    "libx264 (CPU)":         {"vcodec": "libx264",       "pix_fmt": "yuv420p", "crf_max": 51},
    "h264_nvenc (NVIDIA GPU)": {"vcodec": "h264_nvenc",   "pix_fmt": "yuv420p", "crf_max": 51},
    "libx265 (HEVC, CPU)":   {"vcodec": "libx265",       "pix_fmt": "yuv420p", "crf_max": 51},
    "hevc_nvenc (NVIDIA GPU)": {"vcodec": "hevc_nvenc",  "pix_fmt": "yuv420p", "crf_max": 51},
    "libvpx-vp9 (CPU)":      {"vcodec": "libvpx-vp9",    "pix_fmt": "yuv420p", "crf_max": 63},
    "None": None
}

_encoder_cache = {}

def encoder_available(codec):
    if not codec:
        return True
    if codec in _encoder_cache:
        return _encoder_cache[codec]
    available = True
    try:
        (ffmpeg.input('color=c=black:s=320x240:d=0.1', f='lavfi')
               .output(os.devnull, format='null', vcodec=codec, pix_fmt='yuv420p', frames=1)
               .overwrite_output().run(quiet=True))
    except Exception:
        available = False
    _encoder_cache[codec] = available
    return available

FFTWindows = {"Hann": numpy.hanning, "Hamming": numpy.hamming, "Blackman": numpy.blackman, "Bartlett": numpy.bartlett, "Rectangular": numpy.ones}
BarLayouts = {"Horizontal": None, "Vertical": None, "Radial": None}
ColorStyles = {"Brightness": None, "Solid": None, "Gradient": None, "Rainbow": None}
BGStyles = {"Image": None, "Video": None, "Solid": None, "Gradient": None}
BarPositionModes = {"Auto": None, "Exact": None}
BandMeasures = {"Average": None, "Peak": None, "Single bin": None}
TaperCurves = {"Smooth": None, "Linear": None, "Sharp": None}
FreqScales = {"Logarithmic": None, "Mel": None, "Linear": None}
EncoderSpeeds = {"Fastest": None, "Fast": None, "Balanced": None, "Best": None}

def get_window(name, size):
    window = FFTWindows.get(name, numpy.hanning)
    return window(size)

def assert_empty(text, context):
    if len(text) <= 0:
        raise ValueError(context + " is empty")
def assert_enum(value, enum, context):
    if not value in enum:
        raise ValueError(context + " is invalid")

def format_path(path=os.curdir, initialdir=''):
    try:
        return os.path.relpath(path, os.curdir + initialdir).replace('\\', '/')
    except ValueError:
        return os.path.abspath(path).replace('\\', '/')

def check_num(newval):
    return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5
def check_float(newval):
    return re.match('^[+-]?(?:[0-9]*[.])?[0-9]*$', newval) is not None and len(newval) <= 5

class UserVar:
    def __init__(self, value=None):
        self._value = value
        self._trace = []
    def get(self):
        return self._value
    def set(self, value):
        self._value = value
        for callback in list(self._trace):
            try:
                callback(self._value)
            except Exception:
                traceback.print_exc()
    def trace_add(self, mode, callback):
        self._trace.append(callback)
    def __len__(self):
        return 1

def to_signal_scale(signal):
    if signal < 1:
        signal = 1
    return math.log10(signal)

def hex_to_rgb(color):
    if isinstance(color, (tuple, list)):
        return int(color[0]), int(color[1]), int(color[2])
    if color.startswith('#'):
        color = color[1:]
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

def lerp_rgb(c1, c2, t):
    a = hex_to_rgb(c1)
    b = hex_to_rgb(c2)
    return round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t)

def scale_rgb(rgb, factor):
    return round(max(0, min(255, rgb[0] * factor))), round(max(0, min(255, rgb[1] * factor))), round(max(0, min(255, rgb[2] * factor)))

def hsv_to_rgb(h, s, v):
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

def rainbow_rgb(pos, sat, val, hue_deg=0):
    hue = (hue_deg + pos * 360) % 360
    return hsv_to_rgb(hue / 360, sat, val)

def decode_audio(filepath, start=0.0, end=0.0):
    try:
        input_kwargs = {}
        if start > 0:
            input_kwargs['ss'] = start
        if end > start:
            input_kwargs['t'] = end - start
        data = ffmpeg.input(filepath, **input_kwargs).output('pipe:', format='s16le', acodec='pcm_s16le', ac=2).run(capture_stdout=True, quiet=True)[0]
        signal = numpy.frombuffer(data, dtype=numpy.int16)
        probe = ffmpeg.probe(filepath, select_streams='a:0')
        sample_rate = int(probe['streams'][0]['sample_rate'])
    except Exception:
        traceback.print_exc()
        raise ValueError("Could not decode audio file: " + filepath)
    left = signal[0::2]
    right = signal[1::2]
    return {
        'left': left,
        'right': right,
        'sample_rate': sample_rate,
        'channels': 2,
        'duration': len(left) / sample_rate,
    }

def compute_spectrum(signal, sample_rate, fft_size, overlap, window_name, freq_bins=None, band_edges=None, band_measure='Average'):
    signal = numpy.asarray(signal, dtype=numpy.float32)
    if len(signal) < fft_size:
        signal = numpy.pad(signal, (0, fft_size - len(signal)))
    overlap = float(overlap)
    if overlap > 1.0:
        overlap /= 100.0
    hop = int(fft_size * (1.0 - overlap))
    if hop < 1:
        hop = 1
    n_frames = 1 + (len(signal) - fft_size) // hop
    window = get_window(window_name, fft_size).astype(numpy.float32)
    if freq_bins is not None:
        freq_bins = numpy.asarray(freq_bins)
    n_bins_total = fft_size // 2 + 1
    band_starts = None
    band_stops = None
    if band_edges is not None:
        band_edges = numpy.clip(numpy.asarray(band_edges, dtype=numpy.int64), 0, n_bins_total)
        band_starts = numpy.clip(band_edges[:-1], 0, n_bins_total - 1)
        band_stops = numpy.clip(band_edges[1:], 1, n_bins_total)
        n_out = len(band_starts)
    elif freq_bins is not None:
        n_out = len(freq_bins)
    else:
        n_out = n_bins_total
    magnitudes = numpy.empty((n_frames, n_out), dtype=numpy.float32)
    chunk = 4096
    offsets = numpy.arange(fft_size, dtype=numpy.int64)[None, :]
    for start in range(0, n_frames, chunk):
        stop = min(start + chunk, n_frames)
        idx = offsets + hop * numpy.arange(start, stop, dtype=numpy.int64)[:, None]
        frames = signal[idx] * window
        mag = numpy.abs(numpy.fft.rfft(frames, axis=1)).astype(numpy.float32)
        if band_starts is not None and band_stops is not None:
            if band_measure == 'Peak':
                for b in range(n_out):
                    a = int(band_starts[b])
                    z = int(band_stops[b])
                    if z <= a:
                        z = a + 1
                    magnitudes[start:stop, b] = mag[:, a:z].max(axis=1)
            else:
                power = numpy.square(mag)
                for b in range(n_out):
                    a = int(band_starts[b])
                    z = int(band_stops[b])
                    if z <= a:
                        z = a + 1
                    magnitudes[start:stop, b] = numpy.sqrt(power[:, a:z].mean(axis=1))
        elif freq_bins is not None:
            magnitudes[start:stop] = mag[:, freq_bins]
        else:
            magnitudes[start:stop] = mag
    frequencies = numpy.fft.rfftfreq(fft_size, 1 / sample_rate)
    times = (numpy.arange(n_frames) * hop + fft_size / 2) / sample_rate
    return magnitudes, frequencies, times

def bass_boost_gains(frequencies, amount, crossover):
    return 1 + amount * numpy.exp(-numpy.asarray(frequencies, dtype=numpy.float64) / crossover)

def format_eta(seconds):
    seconds = int(max(float(seconds), 0.0))
    if seconds >= 3600:
        return '{}:{:02d}:{:02d}'.format(seconds // 3600, (seconds % 3600) // 60, seconds % 60)
    return '{}:{:02d}'.format(seconds // 60, seconds % 60)

def format_size(num_bytes):
    size = max(float(num_bytes), 0.0)
    unit = 'B'
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size < 1024.0 or unit == 'GB':
            break
        size /= 1024.0
    if unit == 'B':
        return '{:.0f} B'.format(size)
    return '{:.1f} {}'.format(size, unit)