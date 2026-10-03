import math

import numpy

__all__ = ["rms_envelope", "spectral_flux", "detect_beats", "beat_envelope"]

_FFT_SIZE = 1024
_THRESHOLD_K = 1.5
_ONSET_WINDOW_SECONDS = 0.35

def _positive_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number <= 0.0:
        return None
    return number

def _frame_count(value):
    try:
        count = int(value)
    except (TypeError, ValueError):
        return 0
    return count if count > 0 else 0

def _mono_samples(signal):
    try:
        samples = numpy.asarray(signal, dtype=numpy.float32)
    except (TypeError, ValueError):
        return None
    if samples.ndim > 1:
        samples = samples.mean(axis=tuple(range(1, samples.ndim)))
    samples = numpy.reshape(samples, -1)
    if samples.size and not numpy.all(numpy.isfinite(samples)):
        samples = numpy.nan_to_num(samples, nan=0.0, posinf=0.0, neginf=0.0)
    return samples.astype(numpy.float32, copy=False)

def _onset_envelope(samples, sample_rate, fft_size=_FFT_SIZE):
    fft_size = int(fft_size)
    if fft_size < 2:
        fft_size = _FFT_SIZE
    hop = max(1, fft_size // 2)
    total = samples.size
    if total < fft_size:
        padded = numpy.zeros(fft_size, dtype=numpy.float32)
        padded[:total] = samples
        spectra_count = 1
    else:
        padded = samples
        spectra_count = 1 + (total - fft_size) // hop
    starts = numpy.arange(spectra_count, dtype=numpy.int64)[:, None] * hop
    offsets = numpy.arange(fft_size, dtype=numpy.int64)[None, :]
    frames = padded[starts + offsets]
    window = numpy.hanning(fft_size).astype(numpy.float32)
    magnitude = numpy.abs(numpy.fft.rfft(frames * window, axis=1)).astype(numpy.float32)
    if spectra_count > 1:
        delta = numpy.diff(magnitude, axis=0)
        numpy.maximum(delta, 0.0, out=delta)
        flux = delta.sum(axis=1).astype(numpy.float32)
        envelope = numpy.concatenate((numpy.zeros(1, dtype=numpy.float32), flux))
    else:
        envelope = numpy.zeros(1, dtype=numpy.float32)
    times = (numpy.arange(spectra_count, dtype=numpy.float64) * hop + fft_size / 2.0) / sample_rate
    return envelope, times, hop

def _moving_stats(values, window):
    values = values.astype(numpy.float64, copy=False)
    total = values.size
    window = max(1, int(window))
    cumulative = numpy.concatenate(([0.0], numpy.cumsum(values)))
    cumulative_sq = numpy.concatenate(([0.0], numpy.cumsum(values * values)))
    half = window // 2
    starts = numpy.clip(numpy.arange(total) - half, 0, total)
    ends = numpy.clip(numpy.arange(total) - half + window, 0, total)
    counts = numpy.maximum(ends - starts, 1).astype(numpy.float64)
    means = (cumulative[ends] - cumulative[starts]) / counts
    variances = (cumulative_sq[ends] - cumulative_sq[starts]) / counts - means * means
    numpy.maximum(variances, 0.0, out=variances)
    return means, numpy.sqrt(variances)

def rms_envelope(signal, sample_rate, frame_count):
    count = _frame_count(frame_count)
    out = numpy.zeros(count, dtype=numpy.float32)
    rate = _positive_number(sample_rate)
    samples = _mono_samples(signal)
    if count == 0 or rate is None or samples is None or samples.size == 0:
        return out
    total = samples.size
    frame_index = numpy.arange(total, dtype=numpy.int64) * count // total
    squares = samples * samples
    sums = numpy.bincount(frame_index, weights=squares, minlength=count)[:count]
    sizes = numpy.maximum(numpy.bincount(frame_index, minlength=count)[:count], 1)
    energy = numpy.sqrt(sums / sizes)
    peak = float(energy.max()) if energy.size else 0.0
    if peak > 0.0:
        energy = energy / peak
    numpy.clip(energy, 0.0, 1.0, out=energy)
    out[:] = energy.astype(numpy.float32, copy=False)
    return out

def spectral_flux(signal, sample_rate, frame_count, fft_size=1024):
    count = _frame_count(frame_count)
    out = numpy.zeros(count, dtype=numpy.float32)
    rate = _positive_number(sample_rate)
    samples = _mono_samples(signal)
    if count == 0 or rate is None or samples is None or samples.size == 0:
        return out
    try:
        fft_size = int(fft_size)
    except (TypeError, ValueError):
        return out
    if fft_size < 2:
        return out
    hop = max(1, fft_size // 2)
    total = samples.size
    if total < fft_size:
        padded = numpy.zeros(fft_size, dtype=numpy.float32)
        padded[:total] = samples
        spectra_count = 1
    else:
        padded = samples
        spectra_count = 1 + (total - fft_size) // hop
    starts = numpy.arange(spectra_count, dtype=numpy.int64)[:, None] * hop
    offsets = numpy.arange(fft_size, dtype=numpy.int64)[None, :]
    frames = padded[starts + offsets]
    window = numpy.hanning(fft_size).astype(numpy.float32)
    magnitude = numpy.abs(numpy.fft.rfft(frames * window, axis=1)).astype(numpy.float32)
    if spectra_count > 1:
        delta = numpy.diff(magnitude, axis=0)
        numpy.maximum(delta, 0.0, out=delta)
        flux = delta.sum(axis=1)
        flux = numpy.concatenate((numpy.zeros(1, dtype=numpy.float32), flux.astype(numpy.float32)))
    else:
        flux = numpy.zeros(1, dtype=numpy.float32)
    centers = (numpy.arange(spectra_count, dtype=numpy.float64) * hop + fft_size / 2.0) / rate
    frame_index = numpy.floor(centers / (total / rate) * count).astype(numpy.int64)
    numpy.clip(frame_index, 0, count - 1, out=frame_index)
    accumulated = numpy.bincount(frame_index, weights=flux, minlength=count)[:count]
    peak = float(accumulated.max()) if accumulated.size else 0.0
    if peak > 0.0:
        accumulated = accumulated / peak
    numpy.clip(accumulated, 0.0, 1.0, out=accumulated)
    out[:] = accumulated.astype(numpy.float32, copy=False)
    return out

def detect_beats(signal, sample_rate, sensitivity=1.0, min_gap=0.18):
    rate = _positive_number(sample_rate)
    samples = _mono_samples(signal)
    if rate is None or samples is None or samples.size < 2:
        return []
    try:
        sensitivity = float(sensitivity)
    except (TypeError, ValueError):
        sensitivity = 1.0
    if not math.isfinite(sensitivity) or sensitivity <= 0.0:
        sensitivity = 1.0
    try:
        min_gap = float(min_gap)
    except (TypeError, ValueError):
        min_gap = 0.18
    if not math.isfinite(min_gap) or min_gap < 0.0:
        min_gap = 0.18
    envelope, times, hop = _onset_envelope(samples, rate)
    if envelope.size == 0 or float(envelope.max()) <= 0.0:
        return []
    window_frames = max(3, int(round(_ONSET_WINDOW_SECONDS * rate / hop)))
    local_mean, local_std = _moving_stats(envelope, window_frames)
    threshold = local_mean + (_THRESHOLD_K / sensitivity) * local_std
    previous = numpy.empty_like(envelope)
    previous[0] = -numpy.inf
    previous[1:] = envelope[:-1]
    following = numpy.empty_like(envelope)
    following[-1] = -numpy.inf
    following[:-1] = envelope[1:]
    candidates = numpy.nonzero(
        (envelope > threshold) & (envelope >= previous) & (envelope > following)
    )[0]
    if candidates.size == 0:
        return []
    order = candidates[numpy.argsort(envelope[candidates])[::-1]]
    selected = []
    for index in order:
        time = float(times[index])
        if all(abs(time - float(times[other])) >= min_gap for other in selected):
            selected.append(index)
    selected.sort()
    return [float(times[index]) for index in selected]

def beat_envelope(signal, sample_rate, frame_count, duration, sensitivity=1.0, decay=0.92):
    count = _frame_count(frame_count)
    out = numpy.zeros(count, dtype=numpy.float32)
    if count == 0:
        return out
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        return out
    if not math.isfinite(duration) or duration <= 0.0:
        return out
    try:
        decay = float(decay)
    except (TypeError, ValueError):
        decay = 0.92
    if not math.isfinite(decay) or decay < 0.0:
        decay = 0.92
    if decay > 1.0:
        decay = 1.0
    beats = detect_beats(signal, sample_rate, sensitivity=sensitivity)
    if not beats:
        return out
    beat_times = numpy.asarray(beats, dtype=numpy.float64)
    beat_frames = numpy.floor(beat_times / duration * count).astype(numpy.int64)
    numpy.clip(beat_frames, 0, count - 1, out=beat_frames)
    beat_frames = numpy.unique(beat_frames)
    if decay >= 1.0:
        out[beat_frames[0]:] = 1.0
        return out
    if decay <= 0.0:
        out[beat_frames] = 1.0
        return out
    log_decay = math.log(decay)
    log_gain = numpy.full(count, -numpy.inf, dtype=numpy.float64)
    log_gain[beat_frames] = -log_decay * beat_frames
    numpy.maximum.accumulate(log_gain, out=log_gain)
    log_values = log_decay * numpy.arange(count, dtype=numpy.float64) + log_gain
    numpy.exp(log_values, out=log_values)
    numpy.clip(log_values, 0.0, 1.0, out=log_values)
    out[:] = log_values.astype(numpy.float32)
    return out
