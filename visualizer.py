from import_modules import *
from resources import *
from ui import *

import subprocess
import shutil
import time
from typing import cast

try:
    import effects
except Exception:
    effects = None

try:
    import analysis
except Exception:
    analysis = None

from concurrent.futures import ThreadPoolExecutor

HEADLESS = any(arg in ('--no-ui', '--headless') for arg in sys.argv)

RENDER_WORKERS = None
RENDER_SWITCH_INTERVAL = 0.002
ENCODER_THREADS = None

OPTION_NAMES = (
    "input_file", "batch_files", "batch_mode", "export_file", "export_auto", "preview_position",
    "output_format", "encoder", "encoder_speed", "quality", "max_output_size", "audio_copy",
    "video_upscale", "framerate", "resolution_width", "resolution_height",
    "audio_start", "audio_end",
    "channel_pan", "gain_db", "normalize", "bass_boost", "bass_crossover",
    "fft_size", "fft_overlap", "fft_window", "band_measure", "freq_scale", "log_freq", "freq_min", "freq_max", "noise_floor", "db_range",
    "spectral_tilt", "timing_offset", "vocal_boost", "vocal_center", "vocal_width",
    "edge_taper", "edge_taper_left", "edge_taper_right", "edge_taper_curve",
    "smoothing_enabled", "attack_alpha", "decay_alpha", "decay_fast",
    "bars", "bar_layout", "bar_spacing", "coverage_x", "coverage_y",
    "bar_justify_x", "bar_justify_y", "mirror", "bar_scale", "height_exp", "brightness_exp",
    "corner_radius", "outline_width", "outline_color",
    "bar_peak_caps", "bar_peak_size",
    "bar_position_mode", "bar_position_x", "bar_position_y",
    "bar_reflection", "reflection_strength",
    "radial_radius", "radial_thickness", "radial_start", "radial_sweep", "radial_margin", "radial_rotation",
    "color_style", "color_a", "color_b", "color_stops",
    "rainbow_saturation", "rainbow_hue", "rainbow_cycles",
    "effect_glow", "glow_radius", "glow_strength", "effect_trails", "trail_alpha", "trail_scale",
    "post_effect", "post_effect_strength", "beat_pulse", "beat_pulse_strength",
    "background", "bg_style", "bg_solid_color", "bg_grad_a", "bg_grad_b", "bg_stops", "bg_transparent",
    "bg_darken", "bg_blur",
    "bg_zoom", "bg_zoom_amount", "bg_zoom_cycles", "bg_pan", "bg_pan_x", "bg_pan_y", "bg_pan_speed",
    "bg_blur_pulse", "bg_blur_amount", "bg_blur_response",
    "waveform_toggle", "waveform_color", "waveform_opacity", "waveform_scale", "waveform_style", "waveform_window",
    "title_toggle", "title_text", "title_color", "title_size", "title_x", "title_y",
    "watermark_toggle", "watermark_file", "watermark_size", "watermark_blending", "watermark_x", "watermark_y",
)

DEFAULT_ENCODERS = {
    "MP4": "libx264",
    "WebM": "libvpx-vp9",
    "GIF": "gif"
}

_preview_photo = None
_preview_image = None
_preview_after_id = None
_preview_cache_key = None
_preview_cache_ctx = None


def _preview_key(params):
    return tuple(sorted((name, str(value)) for name, value in params.items() if name != 'preview_position'))

_ui_queue = queue.Queue()


def snapshot_values():
    return {name: get_value(name) for name in OPTION_NAMES}


def _safe_rgb(value):
    try:
        rgb = hex_to_rgb(value)
        return (
            max(0, min(255, int(rgb[0]))),
            max(0, min(255, int(rgb[1]))),
            max(0, min(255, int(rgb[2]))),
        )
    except Exception:
        return None


def parse_stops(raw, fallback_a, fallback_b):
    entries = []
    data = None
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except Exception:
            data = None
    elif isinstance(raw, (list, tuple)):
        data = raw
    if isinstance(data, (list, tuple)):
        for item in data:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            try:
                position = float(item[0])
            except (TypeError, ValueError):
                continue
            if not math.isfinite(position):
                continue
            rgb = _safe_rgb(item[1])
            if rgb is None:
                continue
            entries.append((min(1.0, max(0.0, position)), rgb))
    if not entries:
        first = _safe_rgb(fallback_a)
        second = _safe_rgb(fallback_b)
        if first is None:
            first = (255, 255, 255)
        if second is None:
            second = first
        entries = [(0.0, first), (1.0, second)]
    entries.sort(key=lambda entry: entry[0])
    stops = []
    for position, rgb in entries:
        if stops and position - stops[-1][0] <= 1e-6:
            continue
        stops.append((position, rgb))
    if stops[0][0] > 0.0:
        stops.insert(0, (0.0, stops[0][1]))
    if stops[-1][0] < 1.0:
        stops.append((1.0, stops[-1][1]))
    return stops


def sample_stops(stops, t):
    if not stops:
        return (255, 255, 255)
    try:
        t = float(t)
    except (TypeError, ValueError):
        return stops[-1][1]
    if t <= stops[0][0]:
        return stops[0][1]
    if t >= stops[-1][0]:
        return stops[-1][1]
    for index in range(1, len(stops)):
        p1, c1 = stops[index]
        if t <= p1:
            p0, c0 = stops[index - 1]
            span = p1 - p0
            if span <= 0.0:
                return c1
            f = (t - p0) / span
            return (
                int(round(c0[0] + (c1[0] - c0[0]) * f)),
                int(round(c0[1] + (c1[1] - c0[1]) * f)),
                int(round(c0[2] + (c1[2] - c0[2]) * f)),
            )
    return stops[-1][1]


def _build_color_lut(stops, brightness_exp, count=512):
    lut = []
    for index in range(count):
        level = index / float(count - 1)
        lut.append(scale_rgb(sample_stops(stops, level), level ** brightness_exp))
    return lut


def _gradient_image(W, H, stops, count=256):
    lut = numpy.empty((count, 3), dtype=numpy.float32)
    for index in range(count):
        lut[index] = sample_stops(stops, index / float(count - 1))
    if H == count:
        rows = lut.astype(numpy.uint8)
    else:
        positions = numpy.linspace(0.0, count - 1.0, H)
        lower = numpy.floor(positions).astype(numpy.int64)
        upper = numpy.minimum(lower + 1, count - 1)
        frac = (positions - lower)[:, None]
        rows = numpy.clip(numpy.round(lut[lower] * (1.0 - frac) + lut[upper] * frac), 0.0, 255.0).astype(numpy.uint8)
    return Image.fromarray(numpy.repeat(rows[:, None, :], W, axis=1), 'RGB')


def _build_bar_pre(params, bars, W, H):
    layout = params['bar_layout']
    if layout == 'Radial':
        radius = min(W, H) / 2.0
        r0 = radius * float(params['radial_radius'])
        r1 = radius * float(params['coverage_y'])
        sweep = float(params['radial_sweep'])
        angle_half = (sweep / bars - float(params['radial_margin'])) / 2.0
        return {
            'r0': r0,
            'dr': r1 - r0,
            'start_deg': float(params['radial_start']),
            'rot': float(params['radial_rotation']),
            'offsets': [math.radians(sweep / bars * (b + 0.5)) for b in range(bars)],
            'half_rad': math.radians(angle_half),
        }
    spacing_min = math.floor(float(params['bar_spacing']) / 2.0)
    spacing_max = math.ceil(float(params['bar_spacing']) / 2.0)
    if layout == 'Vertical':
        gap = 1.0 - float(params['coverage_y'])
        inc = float(params['coverage_y']) / bars
        justify = float(params['bar_justify_y'])
        return {
            'u0': [(gap * justify + inc * b) * H + spacing_min for b in range(bars)],
            'u1': [(gap * justify + inc * (b + 1)) * H - spacing_max for b in range(bars)],
            'justify': float(params['bar_justify_x']),
            'len_scale': float(params['coverage_x']) * float(params['bar_scale']),
        }
    gap = 1.0 - float(params['coverage_x'])
    inc = float(params['coverage_x']) / bars
    justify = float(params['bar_justify_x'])
    return {
        'u0': [(gap * justify + inc * b) * W + spacing_min for b in range(bars)],
        'u1': [(gap * justify + inc * (b + 1)) * W - spacing_max for b in range(bars)],
        'justify': float(params['bar_justify_y']),
        'len_scale': float(params['coverage_y']) * float(params['bar_scale']),
    }


def _ui(callback):
    if HEADLESS:
        return
    _ui_queue.put(callback)


def _drain_ui():
    while True:
        try:
            callback = _ui_queue.get_nowait()
        except queue.Empty:
            break
        try:
            callback()
        except Exception:
            traceback.print_exc()
    schedule(50, _drain_ui)


def _validate(title='Render settings invalid'):
    ok, problems = validate_settings()
    if ok:
        return True
    messages = [message for _, message in problems]
    print(title + ':')
    for message in messages:
        print(' - ' + message)
    try:
        highlight_invalid([name for name, _ in problems])
    except Exception:
        pass
    if not HEADLESS:
        show_error(title, '\n'.join(messages))
    return False


def _benchmark_fps(ctx, frames=24):
    if ctx['params']['output_format'] == 'PNG sequence':
        return None
    path = os.path.join('export', '_estimate_bench' + export_extension(ctx['params']['output_format']))
    frame_count = max(ctx['frame_count'], 1)
    process = start_encoder(ctx, path)
    if process is None:
        return None
    indices = [min(frame_count - 1, int(frame_count * (0.3 + 0.4 * i / max(frames - 1, 1)))) for i in range(frames)]
    workers = RENDER_WORKERS or max(2, min((os.cpu_count() or 4) // 2, 12))
    workers = max(1, int(workers))

    def render_frame(index):
        image = draw_frame(ctx, index)
        if image is None:
            return None
        return image.tobytes()

    start = timeit.default_timer()
    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for blob in executor.map(render_frame, indices):
                if blob is None:
                    return None
                process.stdin.write(blob)
    except (BrokenPipeError, OSError):
        return None
    finally:
        try:
            process.stdin.close()
        except Exception:
            pass
        try:
            process.wait()
        except Exception:
            pass
    elapsed = timeit.default_timer() - start
    try:
        os.remove(path)
    except OSError:
        pass
    if elapsed <= 0.0:
        return None
    return min(frames / elapsed, 300.0)


def _estimate_fps(params):
    cache_ctx = _preview_cache_ctx
    if cache_ctx is not None and _preview_cache_key == _preview_key(params):
        measured = _benchmark_fps(cache_ctx)
        if measured:
            return measured, True
    W = int(params['resolution_width']) or 1280
    H = int(params['resolution_height']) or 720
    fps = 100.0 * (1280.0 * 720.0) / max(W * H, 1)
    if params['effect_glow']:
        fps *= 0.55
    if params['effect_trails']:
        fps *= 0.8
    if params['bg_blur_pulse']:
        fps *= 0.7
    if params['bar_reflection']:
        fps *= 0.85
    if params.get('post_effect') and params['post_effect'] != 'None':
        fps *= 0.5
    bars = max(int(params['bars']), 1)
    fps *= (32.0 / bars) ** 0.15
    return max(fps, 0.5), False


def _estimate_render(params):
    files = [params['input_file']]
    if params['batch_mode'] and params['batch_files']:
        batch = [part.strip() for part in str(params['batch_files']).split('|') if part.strip()]
        if batch:
            files = batch
    framerate = _num(params.get('framerate'), 30.0) or 30.0
    start_time = _num(params.get('audio_start'), 0.0)
    end_time = _num(params.get('audio_end'), 0.0)
    total = 0.0
    for filepath in files:
        try:
            probe = ffmpeg.probe(resolve_path(filepath))
            duration = float(probe.get('format', {}).get('duration') or 0.0)
        except Exception:
            duration = 0.0
        if end_time > start_time:
            duration = min(duration, end_time) - start_time
        total += max(duration, 0.0)
    frames = total * framerate
    fps, measured = _estimate_fps(params)
    return frames, frames / max(fps, 1e-9), measured


def _confirm_start(message):
    if HEADLESS:
        return True
    box = QtWidgets.QMessageBox(root)
    box.setWindowTitle('Estimated render time')
    box.setText(message)
    box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
    box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)
    return box.exec() == QtWidgets.QMessageBox.StandardButton.Yes


def start_render(preview=False):
    if not _validate():
        return
    params = snapshot_values()
    if not preview and not HEADLESS:
        frames, seconds, measured = _estimate_render(params)
        if frames < 1:
            message = 'Could not estimate the render time.\n\nStart the render?'
        else:
            note = 'measured on this machine' if measured else 'rough estimate'
            message = 'Estimated render time: ~{}\n{} frames at {:.1f} fps ({})\n\nStart the render?'.format(
                format_eta(seconds), int(round(frames)), frames / max(seconds, 1e-9), note)
        if not _confirm_start(message):
            return
    Thread(target=render, args=(preview, params)).start()


def resolve_path(path):
    if os.path.exists(path):
        return path
    joined = os.path.join('files', path)
    if os.path.exists(joined):
        return joined
    return path


def load_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype('arial.ttf', int(size))
    except Exception:
        try:
            return ImageFont.load_default(int(size))
        except TypeError:
            try:
                return ImageFont.load_default()
            except Exception:
                return None


def _codec_name(enc):
    if isinstance(enc, dict):
        return enc.get('vcodec')
    if not enc:
        return None
    return str(enc).split(' (')[0]


def export_extension(output_format):
    return {"MP4": ".mp4", "WebM": ".webm", "GIF": ".gif", "PNG sequence": ""}.get(output_format, ".mp4")


def export_name_for(filepath, output_format, params):
    stem = os.path.splitext(os.path.basename(filepath))[0]
    if params['export_auto'] or not params['export_file']:
        base = 'export_' + stem
    else:
        base = params['export_file']
    return base + export_extension(output_format)


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def read_encoder_progress(path):
    if not path:
        return None, None
    try:
        size = os.path.getsize(path)
        with open(path, 'r', encoding='utf-8', errors='ignore') as handle:
            if size > 2048:
                handle.seek(size - 2048)
            text = handle.read()
    except OSError:
        return None, None
    fps = None
    speed = None
    for line in text.splitlines():
        if line.startswith('fps='):
            try:
                fps = float(line[4:])
            except ValueError:
                pass
        elif line.startswith('speed='):
            try:
                speed = float(line[6:].strip().rstrip('x'))
            except ValueError:
                pass
    return fps, speed


def _extract_video_background(path, W, H, render_fps, interrupt_state=None):
    cache_dir = os.path.join('export', '_bgvideo_{}'.format(int(timeit.default_timer() * 1000)))
    os.makedirs(cache_dir, exist_ok=True)
    fps = max(1.0, float(render_fps))
    duration = 0.0
    try:
        probe = ffmpeg.probe(path)
        duration = float(probe.get('format', {}).get('duration') or 0.0)
    except Exception:
        duration = 0.0
    if duration > 0.0 and duration * fps > 15000:
        fps = max(4.0, 15000.0 / duration)
    process = (
        ffmpeg.input(path)
        .filter('fps', fps=fps)
        .filter('scale', W, H, force_original_aspect_ratio='increase')
        .filter('crop', W, H)
        .output(os.path.join(cache_dir, 'bg_%06d.jpg'), **{'q:v': 3})
        .overwrite_output()
        .run_async(quiet=True)
    )
    while process.poll() is None:
        if interrupt_state and interrupt_state.get('interrupt'):
            try:
                process.kill()
            except Exception:
                pass
            break
        time.sleep(0.1)
    return cache_dir, fps


def _make_video_provider(cache_dir, video_fps, render_fps, W, H):
    names = sorted(name for name in os.listdir(cache_dir)
                   if name.startswith('bg_') and name.endswith('.jpg'))
    paths = [os.path.join(cache_dir, name) for name in names]
    cache = {}
    step = max(1.0, float(video_fps)) / max(1.0, float(render_fps))

    def provider(frame_no):
        if not paths:
            return Image.new('RGB', (W, H), (0, 0, 0))
        index = int(frame_no * step) % len(paths)
        image = cache.get(index)
        if image is None:
            if len(cache) >= 16:
                cache.clear()
            image = Image.open(paths[index]).convert('RGB')
            cache[index] = image
        return image

    return provider


def draw_bar_shape(draw, geometry, fill, params, outline=None, owidth=0):
    coords, kind = geometry
    if kind == 'circle':
        cx, cy, radius = coords
        box = (cx - radius, cy - radius, cx + radius, cy + radius)
        if outline is not None:
            draw.ellipse(box, fill=fill, outline=outline)
        else:
            draw.ellipse(box, fill=fill)
        return
    if kind == 'polygon':
        if outline is not None:
            draw.polygon(coords, fill=fill, outline=outline)
        else:
            draw.polygon(coords, fill=fill)
        return
    x0, y0, x1, y1 = coords
    if x1 <= x0 or y1 <= y0:
        return
    if outline is not None and owidth > 0:
        kwargs = {'outline': outline, 'width': owidth}
    else:
        kwargs = {'outline': None}
    radius = int(params['corner_radius']) if params['corner_radius'] else 0
    if radius > 0:
        radius = min(radius, int((x1 - x0) / 2), int((y1 - y0) / 2))
        if radius > 0:
            draw.rounded_rectangle(coords, radius=radius, fill=fill, **kwargs)
            return
    draw.rectangle(coords, fill=fill, **kwargs)


def bar_geometry(ctx, b, level, t):
    params = ctx['params']
    layout = params['bar_layout']
    if layout == 'Radial':
        return radial_geometry(ctx, b, level, t)
    pre = ctx.get('bar_pre')
    if pre is None:
        pre = _build_bar_pre(params, ctx['bars'], ctx['W'], ctx['H'])
    if params['mirror']:
        length = pre['len_scale'] * (float(level) ** float(params['height_exp']))
        if layout == 'Vertical':
            center = pre['justify'] * ctx['W']
            span = length * ctx['W']
            x0 = max(0.0, center - span / 2.0)
            x1 = min(float(ctx['W']), center + span / 2.0)
            y0 = pre['u0'][b]
            y1 = pre['u1'][b]
        else:
            center = pre['justify'] * ctx['H']
            span = length * ctx['H']
            y0 = max(0.0, center - span / 2.0)
            y1 = min(float(ctx['H']), center + span / 2.0)
            x0 = pre['u0'][b]
            x1 = pre['u1'][b]
        return _apply_exact_position(ctx, ((x0, y0, x1, y1), 'rect'))
    u0 = pre['u0'][b]
    u1 = pre['u1'][b]
    length = pre['len_scale'] * (float(level) ** float(params['height_exp']))
    length_gap = 1.0 - length
    if layout == 'Vertical':
        x0 = length_gap * pre['justify'] * ctx['W']
        x1 = (length_gap * pre['justify'] + length) * ctx['W']
        return _apply_exact_position(ctx, ((x0, u0, x1, u1), 'rect'))
    y0 = length_gap * pre['justify'] * ctx['H']
    y1 = (length_gap * pre['justify'] + length) * ctx['H']
    return _apply_exact_position(ctx, ((u0, y0, u1, y1), 'rect'))


def _apply_exact_position(ctx, geometry):
    params = ctx['params']
    if params['bar_position_mode'] != 'Exact':
        return geometry
    dx = ctx.get('exact_dx')
    dy = ctx.get('exact_dy')
    if dx is None or dy is None:
        dx = (float(params['bar_position_x']) / 100.0 - float(params['bar_justify_x'])) * ctx['W']
        dy = (float(params['bar_position_y']) / 100.0 - float(params['bar_justify_y'])) * ctx['H']
    return _translate_geometry(geometry, -dx, -dy)


def peak_cap_geometry(ctx, b, peak, t):
    params = ctx['params']
    layout = params['bar_layout']
    if layout == 'Radial':
        return []
    rect = bar_geometry(ctx, b, peak, t)
    if not rect or rect[1] != 'rect':
        return []
    x0, y0, x1, y1 = cast(tuple, rect[0])
    size = max(1.0, float(params['bar_peak_size']))
    mirror = bool(params['mirror'])
    if layout == 'Vertical':
        if mirror:
            return [(x0, y0, min(x1, x0 + size), y1), (max(x0, x1 - size), y0, x1, y1)]
        if float(params['bar_justify_x']) < 0.5:
            return [(max(x0, x1 - size), y0, x1, y1)]
        return [(x0, y0, min(x1, x0 + size), y1)]
    if mirror:
        return [(x0, y0, x1, min(y1, y0 + size)), (x0, max(y0, y1 - size), x1, y1)]
    if float(params['bar_justify_y']) >= 0.5:
        return [(x0, y0, x1, min(y1, y0 + size))]
    return [(x0, max(y0, y1 - size), x1, y1)]


def radial_geometry(ctx, b, level, t):
    params = ctx['params']
    pre = ctx.get('bar_pre')
    if pre is None or 'offsets' not in pre:
        pre = _build_bar_pre(params, ctx['bars'], ctx['W'], ctx['H'])
    cx = ctx['W'] / 2.0
    cy = ctx['H'] / 2.0
    r0 = pre['r0']
    length = min(1.0, (float(level) ** float(params['height_exp'])) * float(params['bar_scale']))
    r1 = r0 + pre['dr'] * length
    if r1 <= r0:
        r1 = r0 + 2.0
    start = math.radians(pre['start_deg'] + pre['rot'] * 360.0 * t)
    angle = start + pre['offsets'][b]
    a0 = angle - pre['half_rad']
    a1 = angle + pre['half_rad']
    points = [
        (cx + r0 * math.cos(a0), cy + r0 * math.sin(a0)),
        (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1)),
        (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1)),
        (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0)),
    ]
    return (points, 'polygon')


def radial_thumb(ctx, b, level, t):
    params = ctx['params']
    thickness = float(params['radial_thickness'])
    if thickness <= 0:
        return None
    pre = ctx.get('bar_pre')
    if pre is None or 'offsets' not in pre:
        pre = _build_bar_pre(params, ctx['bars'], ctx['W'], ctx['H'])
    cx = ctx['W'] / 2.0
    cy = ctx['H'] / 2.0
    length = min(1.0, (float(level) ** float(params['height_exp'])) * float(params['bar_scale']))
    r_tip = pre['r0'] + pre['dr'] * length
    start = math.radians(pre['start_deg'] + pre['rot'] * 360.0 * t)
    angle = start + pre['offsets'][b]
    return ((cx + r_tip * math.cos(angle), cy + r_tip * math.sin(angle), thickness / 2.0), 'circle')


def reflect_geometry(ctx, geometry):
    coords, kind = geometry
    if kind == 'polygon':
        return None
    x0, y0, x1, y1 = coords
    layout = ctx['params']['bar_layout']
    mirror = bool(ctx['params']['mirror'])
    if layout == 'Vertical':
        if mirror:
            return ((x0, 2 * y0 - y1, x1, y0), 'rect')
        return ((2 * x0 - x1, y0, x0, y1), 'rect')
    if mirror:
        return ((2 * x0 - x1, y0, x0, y1), 'rect')
    return ((x0, 2 * y0 - y1, x1, y0), 'rect')


def bar_fill_color(ctx, b, level):
    params = ctx['params']
    style = params['color_style']
    if style == 'Brightness':
        lut = ctx.get('bar_lut')
        if lut is None:
            base = sample_stops(ctx.get('bar_stops') or [], float(level))
            return scale_rgb(base, float(level) ** float(params['brightness_exp']))
        index = int(round(float(level) * (len(lut) - 1)))
        if index < 0:
            index = 0
        elif index >= len(lut):
            index = len(lut) - 1
        return lut[index]
    if style == 'Gradient':
        colors = ctx.get('base_colors')
        if colors:
            base = colors[b]
        else:
            base = sample_stops(ctx.get('bar_stops') or [], b / max(ctx['bars'] - 1, 1))
        return scale_rgb(base, float(level) ** float(params['brightness_exp']))
    if style == 'Solid':
        base = ctx.get('solid_color')
        if base is None:
            base = ctx['color_a_rgb']
        return scale_rgb(base, float(level) ** float(params['brightness_exp']))
    if style == 'Rainbow':
        base = ctx['base_colors'][b]
        return scale_rgb(base, float(level) ** float(params['brightness_exp']))
    return (255, 255, 255)


def prepare_context(filepath, params, preview=False, interrupt_state=None):
    interrupt_state = interrupt_state or {'interrupt': False}

    audio = decode_audio(filepath, float(params['audio_start']), float(params['audio_end']) or 0.0)
    sample_rate = int(audio['sample_rate'])
    duration = float(audio['duration'])
    left = audio['left']
    right = audio['right'] if audio['channels'] > 1 else left
    pan = float(params['channel_pan'])
    sig = (numpy.abs(left.astype(numpy.float32) * pan + right.astype(numpy.float32) * (1.0 - pan))).astype(numpy.float32)
    if params['normalize']:
        peak = float(numpy.abs(sig).max())
        if peak > 0.0:
            sig *= (0.95 * 32767.0) / peak
    sig *= math.pow(10.0, float(params['gain_db']) / 20.0)

    framerate = float(params['framerate'])
    bars = int(params['bars'])
    if bars < 1:
        raise ValueError('Number of bars must be at least 1.')
    frame_count = int(duration * framerate)
    if frame_count < 1:
        raise ValueError('Audio is too short for the requested framerate (0 frames to render).')

    frequencies = numpy.fft.rfftfreq(int(params['fft_size']), 1 / sample_rate)
    freq_min = max(float(params['freq_min']), 1.0)
    freq_max = max(float(params['freq_max']), freq_min * 1.001)
    scale = params.get('freq_scale') or ''
    if not scale:
        scale = 'Logarithmic' if params.get('log_freq', True) else 'Linear'
    if scale == 'Linear':
        barfreqs = numpy.linspace(freq_min, freq_max, bars)
    elif scale == 'Mel':
        mel_min = 2595.0 * math.log10(1.0 + freq_min / 700.0)
        mel_max = 2595.0 * math.log10(1.0 + freq_max / 700.0)
        mel_points = numpy.linspace(mel_min, mel_max, bars)
        barfreqs = 700.0 * (numpy.power(10.0, mel_points / 2595.0) - 1.0)
    else:
        barfreqs = numpy.exp(numpy.linspace(math.log(freq_min), math.log(freq_max), bars))
    bin_index = numpy.searchsorted(frequencies, barfreqs)
    bin_index = numpy.clip(bin_index, 0, len(frequencies) - 1)
    band_measure = params.get('band_measure') or 'Average'
    band_edges = None
    if band_measure != 'Single bin' and bars + 1 <= len(frequencies):
        edges = numpy.empty(bars + 1, dtype=numpy.int64)
        edges[0] = int(bin_index[0])
        for band in range(1, bars):
            edges[band] = max(edges[band - 1] + 1, int(bin_index[band]))
        if edges[bars - 1] < len(frequencies):
            edges[bars] = len(frequencies)
            band_edges = edges
    magnitudes, frequencies, times = compute_spectrum(
        sig, sample_rate, int(params['fft_size']), float(params['fft_overlap']), params['fft_window'],
        freq_bins=bin_index, band_edges=band_edges,
        band_measure=params.get('band_measure') or 'Average')
    nframes = len(magnitudes)
    gains = bass_boost_gains(frequencies, float(params['bass_boost']), float(params['bass_crossover']))
    raw = magnitudes * gains[bin_index]
    tilt = _num(params.get('spectral_tilt'), 0.0)
    if tilt != 0.0:
        ref = max(freq_min, 1.0)
        octaves = numpy.log2(numpy.maximum(barfreqs, ref) / ref)
        raw = (raw * (10.0 ** (tilt * octaves / 20.0))[None, :]).astype(numpy.float32)
    vocal_boost = _num(params.get('vocal_boost'), 0.0)
    if vocal_boost != 0.0:
        vocal_center = _num(params.get('vocal_center'), 1200.0)
        vocal_width = max(_num(params.get('vocal_width'), 1.6), 0.1)
        bell = numpy.exp(-0.5 * (numpy.log2(numpy.maximum(barfreqs, 1.0) / max(vocal_center, 1.0)) / vocal_width) ** 2)
        raw = (raw * (10.0 ** (vocal_boost * bell / 20.0))[None, :]).astype(numpy.float32)
    peak_signal = float(raw.max())
    noise_floor = float(params['noise_floor'])
    db_range = float(params['db_range'])
    if peak_signal <= 0.0:
        db = numpy.full(raw.shape, noise_floor - db_range, dtype=numpy.float32)
    else:
        db = 20.0 * numpy.log10(raw / peak_signal + 1e-10)
    levels = numpy.clip((db - noise_floor) / db_range, 0.0, 1.0).astype(numpy.float32)
    del magnitudes, raw, db
    if nframes != frame_count:
        if nframes < 2:
            levels = numpy.repeat(levels[:1], frame_count, axis=0)
        elif frame_count < 2:
            levels = levels[:1]
        else:
            x_old = numpy.linspace(0.0, 1.0, nframes)
            x_new = numpy.linspace(0.0, 1.0, frame_count)
            levels = numpy.stack(
                [numpy.interp(x_new, x_old, levels[:, b]) for b in range(bars)], axis=1).astype(numpy.float32)

    ramp = 60.0 / max(float(framerate), 1.0)
    if params['smoothing_enabled']:
        attack = 1.0 - math.pow(max(1.0 - float(params['attack_alpha']), 1e-6), ramp)
        decay = 1.0 - math.pow(max(1.0 - float(params['decay_alpha']), 1e-6), ramp)
        fast_alpha = min(0.95, float(params['decay_alpha']) * max(1.0, float(params['decay_fast'])))
        decay_fast = 1.0 - math.pow(max(1.0 - fast_alpha, 1e-6), ramp)
        levels = levels.copy()
        prev = levels[0].copy()
        for f in range(1, frame_count):
            rise = levels[f] > prev
            big_drop = (prev - levels[f]) > 0.15
            alpha = numpy.where(rise, attack, numpy.where(big_drop, decay_fast, decay))
            cur = alpha * levels[f] + (1.0 - alpha) * prev
            levels[f] = cur
            prev = cur

    taper = max(0.0, min(1.0, _num(params.get('edge_taper'), 0.0)))
    if taper > 0.0 and bars > 2 and not preview:
        left_width = max(0.0, min(0.5, _num(params.get('edge_taper_left'), 0.25)))
        right_width = max(0.0, min(0.5, _num(params.get('edge_taper_right'), 0.25)))
        curve = params.get('edge_taper_curve') or 'Smooth'

        def _taper_shape(x):
            x = min(max(x, 0.0), 1.0)
            if curve == 'Linear':
                return x
            if curve == 'Sharp':
                return x * x
            return 0.5 - 0.5 * math.cos(math.pi * x)

        factors = numpy.ones(bars, dtype=numpy.float32)
        left_n = int(round(left_width * (bars - 1)))
        if left_n > 0:
            for b in range(left_n + 1):
                factors[b] = min(factors[b], 1.0 - taper * (1.0 - _taper_shape(b / left_n)))
        right_n = int(round(right_width * (bars - 1)))
        if right_n > 0:
            for b in range(right_n + 1):
                idx = bars - 1 - b
                factors[idx] = min(factors[idx], 1.0 - taper * (1.0 - _taper_shape(b / right_n)))
        levels = (levels * factors[None, :]).astype(numpy.float32)

    offset = _num(params.get('timing_offset'), 0.0)
    shift = int(round(offset * framerate))
    if shift and frame_count > 1:
        shift = max(-(frame_count - 1), min(frame_count - 1, shift))
        if shift > 0:
            tail = numpy.repeat(levels[-1:], shift, axis=0)
            levels = numpy.concatenate([levels[shift:], tail], axis=0)
        else:
            head = numpy.repeat(levels[:1], -shift, axis=0)
            levels = numpy.concatenate([head, levels[:shift]], axis=0)

    peak_step = min(0.95, max(float(params['decay_alpha']), 0.02) * 0.5)
    peak_alpha = 1.0 - math.pow(max(1.0 - peak_step, 1e-6), ramp)
    peaks = numpy.empty_like(levels)
    peaks[0] = levels[0]
    for f in range(1, frame_count):
        fall = peaks[f - 1] * (1.0 - peak_alpha)
        peaks[f] = numpy.maximum(fall, levels[f - 1])

    bass_count = max(1, bars // 4)
    pulse = numpy.mean(levels[:, :bass_count], axis=1).astype(numpy.float32)

    W, H = int(params['resolution_width']), int(params['resolution_height'])
    default_canvas = (1280, 720)
    bg_style = params['bg_style']
    transparent_bg = bool(params.get('bg_transparent')) and params.get('output_format') == 'PNG sequence'
    bg_stops = parse_stops(params.get('bg_stops'), params['bg_grad_a'], params['bg_grad_b'])
    bg_provider = None
    bg_cache_dir = None
    bg_path = ''
    video_darken = 0.0
    video_blur = 0.0
    bg_darken = max(0.0, min(1.0, _num(params.get('bg_darken'), 0.0)))
    bg_blur = max(0.0, _num(params.get('bg_blur'), 0.0))
    if bg_style == 'Video' and not transparent_bg:
        bg_path = params['background']
        if not os.path.exists(bg_path):
            bg_path = os.path.join('files', bg_path)
        if not os.path.exists(bg_path):
            raise ValueError('Background video file not found: ' + str(params['background']))
        if W <= 0 or H <= 0:
            probe = ffmpeg.probe(bg_path)
            stream = next((s for s in probe.get('streams', []) if s.get('codec_type') == 'video'), None)
            W = int((stream or {}).get('width') or default_canvas[0])
            H = int((stream or {}).get('height') or default_canvas[1])
        base_bg = None
    elif bg_style == 'Image' and not transparent_bg:
        bg_path = params['background']
        if not os.path.exists(bg_path):
            bg_path = os.path.join('files', bg_path)
        base_bg = Image.open(bg_path).convert('RGB')
        if W <= 0 or H <= 0:
            W, H = base_bg.size
    elif transparent_bg:
        if W <= 0 or H <= 0:
            W, H = default_canvas
        base_bg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    elif bg_style == 'Solid':
        if W <= 0 or H <= 0:
            W, H = default_canvas
        base_bg = Image.new('RGB', (W, H), hex_to_rgb(params['bg_solid_color']))
    else:
        if W <= 0 or H <= 0:
            W, H = default_canvas
        base_bg = _gradient_image(W, H, bg_stops)

    if bg_style in ('Image', 'Video') and not transparent_bg:
        upscale_target = ResolutionUpscale.get(params['video_upscale'], 0) or 0
        if upscale_target > 0 and min(W, H) < upscale_target:
            scale = upscale_target / float(min(W, H))
            W = int(round(W * scale))
            H = int(round(H * scale))
    if base_bg is None:
        base_bg = Image.new('RGB', (max(int(W), 2), max(int(H), 2)), (0, 0, 0))
    W -= W % 2
    H -= H % 2
    W = max(W, 2)
    H = max(H, 2)
    if bg_style == 'Video' and not transparent_bg:
        def _bg_notice():
            progress_label.configure(text='Preparing background video...')
        _ui(_bg_notice)
        bg_cache_dir, video_fps = _extract_video_background(
            bg_path, W, H, _num(params.get('framerate'), 30.0), interrupt_state)
        bg_provider = _make_video_provider(
            bg_cache_dir, video_fps, _num(params.get('framerate'), 30.0), W, H)
        base_bg = bg_provider(0).copy()
        video_darken = bg_darken
        video_blur = bg_blur
    if transparent_bg:
        bg_static = base_bg.resize((W, H))
    elif bg_style == 'Video':
        bg_static = base_bg
    else:
        if base_bg.width < W or base_bg.height < H:
            base_bg = ImageOps.cover(base_bg, (W, H))
        bg_static = base_bg.resize((W, H))

    if bg_darken > 0.0 and not transparent_bg and bg_style != 'Video':
        factor = tuple([int(round(255 * (1.0 - bg_darken)))] * 3)
        if bg_static.mode == 'RGB':
            bg_static = ImageChops.multiply(bg_static, Image.new('RGB', bg_static.size, factor))
        if base_bg is not None and base_bg.mode == 'RGB':
            base_bg = ImageChops.multiply(base_bg, Image.new('RGB', base_bg.size, factor))
    if bg_blur >= 1.0 and not transparent_bg and bg_style == 'Image':
        radius = int(round(bg_blur))
        bg_static = bg_static.filter(ImageFilter.BoxBlur(radius))
        if base_bg is not None:
            base_bg = base_bg.filter(ImageFilter.BoxBlur(radius))
    try:
        extrema = cast(tuple, bg_static.convert('RGB').getextrema())
        bg_uniform = all(low == high for low, high in extrema)
    except Exception:
        bg_uniform = False
    bar_pre = _build_bar_pre(params, bars, W, H)
    exact_dx = (float(params['bar_position_x']) / 100.0 - float(params['bar_justify_x'])) * W
    exact_dy = (float(params['bar_position_y']) / 100.0 - float(params['bar_justify_y'])) * H

    watermark_layer = None
    blender = None
    if params['watermark_toggle']:
        wm_path = params['watermark_file']
        if not os.path.exists(wm_path):
            wm_path = os.path.join('files', wm_path)
        wm = Image.open(wm_path).convert('RGB')
        target = min(W, H) * float(params['watermark_size'])
        scale = target / max(wm.width, wm.height)
        if scale != 1.0 and scale > 0.0:
            wm = ImageOps.scale(wm, scale)
        layer = Image.new('RGB', (W, H), (0, 0, 0))
        layer.paste(wm, (int(W * float(params['watermark_x']) - wm.width / 2.0),
                         int(H * float(params['watermark_y']) - wm.height / 2.0)))
        watermark_layer = layer
        blender = BlendingModes[params['watermark_blending']]

    color_a_rgb = hex_to_rgb(params['color_a'])
    color_b_rgb = hex_to_rgb(params['color_b'])
    title_rgb = hex_to_rgb(params['title_color'])
    waveform_rgb = hex_to_rgb(params['waveform_color'])
    outline_rgb = hex_to_rgb(params['outline_color'])

    bar_stops = parse_stops(params.get('color_stops'), params['color_a'], params['color_b'])
    base_colors = None
    bar_lut = None
    solid_color = None
    color_style = params['color_style']
    if color_style == 'Brightness':
        bar_lut = _build_color_lut(bar_stops, float(params['brightness_exp']))
    elif color_style == 'Gradient':
        base_colors = []
        for b in range(bars):
            progress = (b / max(bars - 1, 1)) if bars > 1 else 0.0
            base_colors.append(sample_stops(bar_stops, progress))
    elif color_style == 'Solid':
        solid_color = color_a_rgb
    elif color_style == 'Rainbow':
        cycles = max(float(params['rainbow_cycles']), 1.0)
        saturation = float(params['rainbow_saturation'])
        hue = float(params['rainbow_hue'])
        base_colors = []
        for b in range(bars):
            progress = (b / max(bars - 1, 1)) * cycles % 1.0 if bars > 1 else 0.0
            base_colors.append(rainbow_rgb(progress, saturation, 1.0, int(round(hue))))

    wave = None
    if params['waveform_toggle']:
        wave_peak = float(numpy.abs(sig).max()) or 1.0
        wave_amp = float(params['waveform_scale']) * (H / 2.0) / wave_peak
        step = max(1.0, len(sig) / W)
        cols = []
        start_idx = 0
        for i in range(W):
            end_idx = max(int(round((i + 1) * step)), start_idx + 1)
            if start_idx < len(sig):
                chunk = sig[start_idx:min(end_idx, len(sig))]
                cols.append(float(numpy.mean(chunk)) if chunk.size else 0.0)
            else:
                cols.append(0.0)
            start_idx = end_idx
        wave = numpy.asarray(cols, dtype=numpy.float32) * wave_amp

    beat = None
    if params.get('beat_pulse') and analysis is not None:
        try:
            beat = analysis.beat_envelope(sig, sample_rate, frame_count, duration, sensitivity=1.0)
        except Exception:
            beat = None
    del sig

    title_font = load_font(int(params['title_size'])) if params['title_toggle'] else None

    return {
        'params': params,
        'W': W,
        'H': H,
        'bars': bars,
        'framerate': framerate,
        'frame_count': frame_count,
        'duration': duration,
        'sample_rate': sample_rate,
        'audio_path': resolve_path(filepath),
        'levels': levels,
        'peaks': peaks,
        'pulse': pulse,
        'bg_base': base_bg,
        'bg_static': bg_static,
        'bg_uniform': bg_uniform,
        'bg_provider': bg_provider,
        'bg_cache_dir': bg_cache_dir,
        'video_darken': video_darken,
        'video_blur': video_blur,
        'motion': bool(params['bg_zoom'] or params['bg_pan']),
        'watermark_layer': watermark_layer,
        'blender': blender,
        'base_colors': base_colors,
        'bar_stops': bar_stops,
        'bg_stops': bg_stops,
        'bar_lut': bar_lut,
        'solid_color': solid_color,
        'bar_pre': bar_pre,
        'exact_dx': exact_dx,
        'exact_dy': exact_dy,
        'beat': beat,
        'color_a_rgb': color_a_rgb,
        'color_b_rgb': color_b_rgb,
        'outline_rgb': outline_rgb,
        'title_font': title_font,
        'title_rgb': title_rgb,
        'waveform_rgb': waveform_rgb,
        'wave': wave,
        'interrupt_flag': interrupt_state,
    }


def _geometry_bbox(geometry):
    coords, kind = geometry
    if kind == 'rect':
        return coords
    if kind == 'circle':
        cx, cy, radius = coords
        return (cx - radius, cy - radius, cx + radius, cy + radius)
    xs = [point[0] for point in coords]
    ys = [point[1] for point in coords]
    return (min(xs), min(ys), max(xs), max(ys))


def _translate_geometry(geometry, dx, dy):
    coords, kind = geometry
    if kind == 'rect':
        x0, y0, x1, y1 = coords
        return ((x0 - dx, y0 - dy, x1 - dx, y1 - dy), kind)
    if kind == 'circle':
        cx, cy, radius = coords
        return ((cx - dx, cy - dy, radius), kind)
    return ([(x - dx, y - dy) for x, y in coords], kind)


def _bar_bounds(geometry, W, H):
    bx0, by0, bx1, by1 = _geometry_bbox(geometry)
    ix0 = max(int(math.floor(bx0)), 0)
    iy0 = max(int(math.floor(by0)), 0)
    ix1 = min(int(math.ceil(bx1)), W)
    iy1 = min(int(math.ceil(by1)), H)
    return ix0, iy0, ix1, iy1


def draw_frame(ctx, frame_no):
    if ctx['interrupt_flag']['interrupt']:
        return None
    params = ctx['params']
    W = ctx['W']
    H = ctx['H']
    frame_count = ctx['frame_count']
    t = 0.0 if frame_count < 2 else frame_no / float(frame_count - 1)

    beat = ctx.get('beat')
    beat_pulse = 0.0
    if beat is not None:
        try:
            beat_pulse = float(beat[frame_no])
        except Exception:
            beat_pulse = 0.0
    beat_strength = 0.0
    if beat_pulse > 0.0:
        try:
            beat_strength = float(params.get('beat_pulse_strength') or 0.5)
        except (TypeError, ValueError):
            beat_strength = 0.5
    beat_zoom = 0.2 * beat_strength * beat_pulse

    provider = ctx.get('bg_provider')
    if ctx['motion'] or beat_zoom > 0.0:
        zoom = 1.0 + beat_zoom
        if params['bg_zoom']:
            zoom += float(params['bg_zoom_amount']) * (0.5 - 0.5 * math.cos(2.0 * math.pi * float(params['bg_zoom_cycles']) * t))
        if params['bg_pan'] and not params['bg_zoom']:
            zoom = max(zoom, 1.15)
        base = provider(frame_no) if provider is not None else ctx['bg_base']
        win_w = max(int(round(base.width / zoom)), 2)
        win_h = max(int(round(base.height / zoom)), 2)
        if params['bg_pan']:
            ox = float(params['bg_pan_x']) * 0.5 * (1.0 + math.sin(2.0 * math.pi * float(params['bg_pan_speed']) * t))
            oy = float(params['bg_pan_y']) * 0.5 * (1.0 + math.cos(2.0 * math.pi * float(params['bg_pan_speed']) * t))
        else:
            ox = oy = 0.5
        x0 = int((base.width - win_w) * ox)
        y0 = int((base.height - win_h) * oy)
        if win_w == W and win_h == H and x0 == 0 and y0 == 0:
            frame = base.copy()
        else:
            frame = base.crop((x0, y0, x0 + win_w, y0 + win_h)).resize((W, H), Image.Resampling.BILINEAR)
    else:
        if provider is not None:
            frame = provider(frame_no).copy()
        else:
            frame = ctx['bg_static'].copy()

    video_darken = ctx.get('video_darken') or 0.0
    if video_darken > 0.0:
        level = int(round(255 * (1.0 - min(max(video_darken, 0.0), 1.0))))
        frame = ImageChops.multiply(frame, Image.new('RGB', frame.size, (level, level, level)))
    video_blur = ctx.get('video_blur') or 0.0
    if video_blur >= 1.0:
        frame = frame.filter(ImageFilter.BoxBlur(int(round(video_blur))))

    if params['bg_blur_pulse'] and not ctx.get('bg_uniform', False):
        radius = float(params['bg_blur_amount']) * float(ctx['pulse'][frame_no]) * float(params['bg_blur_response'])
        if radius >= 1.0:
            frame = frame.filter(ImageFilter.BoxBlur(int(round(radius))))

    draw = ImageDraw.Draw(frame)
    levels = ctx['levels'][frame_no]
    peaks = ctx['peaks'][frame_no]
    positions = []
    for b in range(ctx['bars']):
        level = float(levels[b])
        peak = float(peaks[b])
        fill = bar_fill_color(ctx, b, level)
        geometry = bar_geometry(ctx, b, level, t)
        if params['effect_trails']:
            trail_level = max(0.0, peak * float(params['trail_scale']))
            if trail_level == level:
                trail_geo = geometry
            else:
                trail_geo = bar_geometry(ctx, b, trail_level, t)
            draw_bar_shape(draw, trail_geo, scale_rgb(fill, float(params['trail_alpha'])), params, None, 0)
        outline = ctx['outline_rgb'] if int(params['outline_width']) > 0 else None
        owidth = int(params['outline_width'])
        draw_bar_shape(draw, geometry, fill, params, outline, owidth)
        if params['bar_peak_caps'] and params['bar_layout'] != 'Radial':
            for cap in peak_cap_geometry(ctx, b, max(level, peak), t):
                draw_bar_shape(draw, (cap, 'rect'), fill, params, None, 0)
        positions.append((geometry, fill))
        if params['bar_layout'] == 'Radial':
            thumb = radial_thumb(ctx, b, level, t)
            if thumb:
                draw_bar_shape(draw, thumb, fill, params, outline, int(params['outline_width']))
                positions.append((thumb, fill))
        if params['bar_reflection'] and params['bar_layout'] != 'Radial':
            reflected = reflect_geometry(ctx, geometry)
            if reflected:
                draw_bar_shape(draw, reflected, scale_rgb(fill, float(params['reflection_strength'])), params, None, 0)

    if params['effect_glow']:
        glow_strength = float(params['glow_strength']) * (1.0 + beat_strength * beat_pulse)
        radius = int(params['glow_radius'])
        box = None
        if positions:
            x0, y0, x1, y1 = _geometry_bbox(positions[0][0])
            for geometry, fill in positions[1:]:
                gx0, gy0, gx1, gy1 = _geometry_bbox(geometry)
                x0 = min(x0, gx0)
                y0 = min(y0, gy0)
                x1 = max(x1, gx1)
                y1 = max(y1, gy1)
            pad = radius * 3 + 4
            bx0 = max(int(math.floor(x0)) - pad, 0)
            by0 = max(int(math.floor(y0)) - pad, 0)
            bx1 = min(int(math.ceil(x1)) + pad, W)
            by1 = min(int(math.ceil(y1)) + pad, H)
            if bx1 - bx0 > 1 and by1 - by0 > 1:
                box = (bx0, by0, bx1, by1)
        if box is not None and frame.mode == 'RGB':
            glow = Image.new('RGB', (box[2] - box[0], box[3] - box[1]), (0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            for geometry, fill in positions:
                draw_bar_shape(glow_draw, _translate_geometry(geometry, box[0], box[1]),
                               scale_rgb(fill, glow_strength), params, None, 0)
            if radius >= 1:
                glow = glow.filter(ImageFilter.BoxBlur(radius))
            region = frame.crop(box)
            frame.paste(ImageChops.add(region, glow), (box[0], box[1]))
        else:
            glow = Image.new('RGB', (W, H), (0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            for geometry, fill in positions:
                draw_bar_shape(glow_draw, geometry, scale_rgb(fill, glow_strength), params, None, 0)
            if radius >= 1:
                glow = glow.filter(ImageFilter.BoxBlur(radius))
            if frame.mode == 'RGBA':
                alpha = frame.getchannel('A')
                frame = ImageChops.add(frame.convert('RGB'), glow).convert('RGBA')
                frame.putalpha(alpha)
            else:
                frame = ImageChops.add(frame, glow)
        draw = ImageDraw.Draw(frame)

    if params['waveform_toggle'] and ctx['wave'] is not None:
        draw = ImageDraw.Draw(frame)
        wave = ctx['wave']
        total = max(ctx['duration'], 1e-9)
        center_time = frame_no / float(ctx['framerate'])
        half = float(params['waveform_window']) / 2.0
        left_t = max(center_time - half, 0.0)
        right_t = min(center_time + half, total)
        i0 = int(left_t / total * W)
        i1 = int(right_t / total * W)
        if i1 > i0:
            i1 = min(i1, W - 1)
            i0 = max(i0, 0)
            if i1 - i0 >= 1:
                ys = wave[i0:i1 + 1]
                if params['waveform_style'] == 'Bounce':
                    ys = H * 1.0 - (ys + float(params['waveform_scale']) * (H / 2.0))
                else:
                    ys = H / 2.0 - ys
                xs = numpy.arange(i0, i1 + 1, dtype=numpy.float32)
                points = list(zip(xs.tolist(), ys.tolist()))
                if len(points) >= 2:
                    draw.line(points, fill=scale_rgb(ctx['waveform_rgb'], float(params['waveform_opacity'])), width=2)

    if params['title_toggle']:
        draw = ImageDraw.Draw(frame)
        draw.text(
            (float(params['title_x']) * W, float(params['title_y']) * H),
            str(params['title_text']), font=ctx['title_font'], fill=ctx['title_rgb'], anchor='mm')

    if ctx['watermark_layer'] is not None:
        if frame.mode == 'RGBA':
            alpha = frame.getchannel('A')
            frame = ctx['blender'](frame.convert('RGB'), ctx['watermark_layer']).convert('RGBA')
            frame.putalpha(alpha)
        else:
            frame = ctx['blender'](frame, ctx['watermark_layer'])

    if effects is not None:
        try:
            frame = effects.apply_post_effect(frame, params.get('post_effect') or 'None', float(params.get('post_effect_strength') or 0.0))
        except Exception:
            pass

    return frame


def _set_low_priority(process):
    if os.name != 'nt':
        return
    try:
        PROCESS_SET_INFORMATION = 0x0200
        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_SET_INFORMATION, False, process.pid)
        if handle:
            kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS)
            kernel32.CloseHandle(handle)
    except Exception:
        pass


def start_encoder(ctx, output_path, progress_path=None):
    params = ctx['params']
    output_format = params['output_format']
    if output_format == 'PNG sequence':
        return None
    W = ctx['W']
    H = ctx['H']
    fps = ctx['framerate']
    video = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(W, H), r=fps)
    enc = Encoders.get(params['encoder'])
    if not enc or params['encoder'] == 'Auto':
        enc = DEFAULT_ENCODERS.get(output_format, 'libx264')
    enc = _codec_name(enc)
    if output_format != 'GIF' and not encoder_available(enc):
        fallback = DEFAULT_ENCODERS.get(output_format, 'libx264')
        print('Encoder "' + str(enc) + '" is not available on this system; using "' + fallback + '" instead.')
        enc = fallback
    if output_format == 'GIF':
        out_kwargs = {'format': 'gif', 'r': fps}
        out = video.output(output_path, **out_kwargs)
    else:
        out_kwargs = {'vcodec': enc, 'pix_fmt': 'yuv420p', 'r': fps}
        crf_max = 63 if output_format == 'WebM' else 51
        crf = int(round(crf_max * ((100.0 - float(params['quality'])) / 100.0) * 1.6))
        out_kwargs['crf'] = max(0, min(crf_max, crf))
        speed = str(params.get('encoder_speed') or 'Fast')
        encoder_threads = ENCODER_THREADS if ENCODER_THREADS is not None else max(2, min((os.cpu_count() or 4), 16))
        if encoder_threads and enc in ('libx264', 'libx265', 'libvpx-vp9'):
            out_kwargs['threads'] = str(encoder_threads)
        if enc in ('libx264', 'libx265'):
            out_kwargs['preset'] = {'Fastest': 'ultrafast', 'Fast': 'veryfast',
                                    'Balanced': 'medium', 'Best': 'slow'}.get(speed, 'veryfast')
        elif enc in ('h264_nvenc', 'hevc_nvenc'):
            out_kwargs['preset'] = {'Fastest': 'p1', 'Fast': 'p3',
                                    'Balanced': 'p5', 'Best': 'p7'}.get(speed, 'p3')
        elif enc == 'libvpx-vp9':
            out_kwargs['deadline'] = 'realtime' if speed == 'Fastest' else 'good'
            out_kwargs['cpu-used'] = {'Fastest': '8', 'Fast': '5',
                                      'Balanced': '2', 'Best': '0'}.get(speed, '5')
        audio_kwargs = {'t': ctx['frame_count'] / fps}
        if float(params['audio_start']) > 0:
            audio_kwargs['ss'] = float(params['audio_start'])
        audio = ffmpeg.input(ctx['audio_path'], **audio_kwargs).audio
        if params['audio_copy'] and output_format == 'MP4':
            copyable = {'aac', 'mp3', 'ac3', 'eac3', 'alac'}
            try:
                probe = ffmpeg.probe(ctx['audio_path'])
                stream = next((s for s in probe.get('streams', []) if s.get('codec_type') == 'audio'), None)
                source_codec = (stream or {}).get('codec_name')
            except Exception:
                source_codec = None
            if source_codec in copyable:
                out_kwargs['acodec'] = 'copy'
            else:
                print('Audio codec "' + str(source_codec) + '" cannot be copied into MP4; re-encoding with AAC.')
        size_cap = _num(params.get('max_output_size'), 0.0)
        duration = ctx['frame_count'] / max(fps, 1e-9)
        if size_cap > 0.0 and duration > 0.0:
            audio_kbps = 0.0 if out_kwargs.get('acodec') == 'copy' else 128.0
            total_kbits = size_cap * 8.0 * 1024.0
            video_kbits = max(total_kbits - audio_kbps * duration, 100.0 * duration)
            maxrate = max(int(video_kbits * 1000.0 / duration), 40000)
            if enc == 'libvpx-vp9':
                out_kwargs['b:v'] = str(maxrate)
            else:
                out_kwargs['maxrate'] = str(maxrate)
                out_kwargs['bufsize'] = str(maxrate * 2)
            if out_kwargs.get('acodec') != 'copy':
                out_kwargs['b:a'] = '128k'
        out_kwargs['shortest'] = None
        if output_format == 'MP4':
            out_kwargs['movflags'] = '+faststart'
        out = ffmpeg.output(video, audio, output_path, **out_kwargs)
    if progress_path:
        out = out.global_args('-progress', progress_path, '-nostats')
    process = out.overwrite_output().run_async(pipe_stdin=True)
    _set_low_priority(process)
    return process


def render(preview=False, params=None):
    if params is None:
        params = snapshot_values()
    state = {'interrupt': False}
    ok = True
    interrupted = False
    old_switch = None
    try:
        old_switch = sys.getswitchinterval()
        if RENDER_SWITCH_INTERVAL:
            sys.setswitchinterval(RENDER_SWITCH_INTERVAL)
    except Exception:
        old_switch = None

    def interrupt():
        state['interrupt'] = True

    files = [params['input_file']]
    if params['batch_mode'] and params['batch_files']:
        batch = [part.strip() for part in str(params['batch_files']).split('|') if part.strip()]
        if batch:
            files = batch
    if preview:
        files = files[:1]

    os.makedirs('export', exist_ok=True)
    output_format = params['output_format']

    progress = {'done': 0, 'total': 0, 'framerate': _num(params.get('framerate'), 30.0) or 30.0,
                'start': timeit.default_timer(), 'bytes': 0}
    last_path = None
    encoder_failed = False
    progress_file = None
    ctx = None

    def render_stats(frames_done):
        elapsed = timeit.default_timer() - progress['start']
        fps = max(frames_done / max(elapsed, 1e-9), 1e-9)
        speed = fps / max(progress.get('framerate') or 30.0, 1e-9)
        eta = max(progress['total'] - frames_done, 0) / fps
        return elapsed, fps, speed, eta

    def progress_texts(frames_done, frames_in_file, frames_this_file, enc_fps=None, enc_speed=None):
        elapsed, fps, speed, eta = render_stats(frames_done)
        percent = 100.0 * frames_done / max(progress['total'], 1)
        estimate = progress['bytes'] / max(frames_in_file, 1) * frames_this_file
        status = '{}%   ETA {}   ~{}'.format(int(round(percent)), format_eta(eta), format_size(estimate))
        if enc_fps is not None and enc_fps > 0:
            status += '   {:.0f} fps'.format(enc_fps)
        label = 'Rendering... ({:.1f}s) - {}/{} - {:.1f}/s - {:.2f}x'.format(
            elapsed, frames_done, progress['total'], fps, speed)
        if enc_fps is not None and enc_fps > 0:
            label += ' - encoder {:.1f} fps'.format(enc_fps)
        return status, label

    try:
        def begin_ui():
            set_ui_state('disabled')
            continue_button.configure(state='normal', text='Cancel', command=interrupt)
        _ui(begin_ui)
        for fi, filepath in enumerate(files):
            if state['interrupt']:
                interrupted = True
                break
            name = os.path.basename(str(filepath or ''))
            _ui(lambda fi=fi, name=name: progress_label.configure(
                text=f'Rendering file {fi + 1}/{len(files)}: {name}'))
            ctx = prepare_context(filepath, params, preview=preview, interrupt_state=state)
            frame_count = ctx['frame_count']
            if frame_count < 1:
                raise ValueError('No frames to render (check audio duration/framerate).')
            progress['total'] += frame_count
            progress['framerate'] = ctx['framerate']
            _ui(lambda: progress_bar.configure(maximum=max(progress['total'] - 1, 1)))

            if preview:
                position = float(params['preview_position'] or 0.0) / 100.0
                idx = max(0, min(frame_count - 1, int(round(position * (frame_count - 1)))))
                image = draw_frame(ctx, idx)
                image.save('export/preview.png')
                if not HEADLESS:
                    _ui(lambda: os.startfile(os.path.abspath('export/preview.png')))
                break

            if len(files) > 1 and not params['export_auto']:
                stem = os.path.splitext(os.path.basename(str(filepath or '')))[0]
                export_name = (params['export_file'] or 'export') + '_' + stem + export_extension(output_format)
            else:
                export_name = export_name_for(filepath, output_format, params)
            export_path = os.path.join('export', export_name)
            last_path = export_path
            seq_folder = ''
            if output_format == 'PNG sequence':
                seq_folder = os.path.splitext(export_name)[0]
                os.makedirs(os.path.join('export', seq_folder), exist_ok=True)
            progress_file = None
            if output_format != 'PNG sequence':
                progress_file = os.path.join('export', '_encprog_{}.txt'.format(int(timeit.default_timer() * 1000)))
                try:
                    if os.path.exists(progress_file):
                        os.remove(progress_file)
                except OSError:
                    pass
            if output_format != 'PNG sequence' and os.path.exists(export_path):
                try:
                    with open(export_path, 'ab'):
                        pass
                except OSError as error:
                    raise RuntimeError('Cannot write to "' + export_path +
                                       '" - is it open in another program? (' + str(error) + ')')
            process = start_encoder(ctx, export_path, progress_path=progress_file)
            frames_written = 0
            progress['bytes'] = 0
            try:
                def render_frame(n):
                    image = draw_frame(ctx, n)
                    if image is None or output_format == 'PNG sequence':
                        return image
                    return image.tobytes()
                workers = RENDER_WORKERS or max(2, min((os.cpu_count() or 4) // 2, 12))
                workers = max(1, int(workers))
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    for i, item in enumerate(executor.map(render_frame, range(frame_count))):
                        if state['interrupt'] or item is None:
                            interrupted = True
                            break
                        if output_format == 'PNG sequence':
                            png_path = os.path.join('export', seq_folder, '{:06d}.png'.format(i))
                            item.save(png_path, compress_level=3)
                            try:
                                progress['bytes'] += os.path.getsize(png_path)
                            except OSError:
                                pass
                        else:
                            try:
                                process.stdin.write(item)
                            except (BrokenPipeError, OSError) as error:
                                code = process.poll()
                                print('Video encoder stopped unexpectedly (exit code {}): {}'.format(code, error))
                                print('Common causes: the output file is open in another program, or the encoder rejected the audio stream.')
                                state['interrupt'] = True
                                encoder_failed = True
                                break
                        progress['done'] += 1
                        frames_written += 1
                        if frames_written % 3 == 0 or frames_written == frame_count:
                            if output_format != 'PNG sequence':
                                try:
                                    progress['bytes'] = os.path.getsize(export_path)
                                except OSError:
                                    pass
                            enc_fps, enc_speed = read_encoder_progress(progress_file)
                            status, label = progress_texts(progress['done'], frames_written, frame_count, enc_fps, enc_speed)
                            _ui(lambda s=status: progress_bar.configure(status=s))
                            _ui(lambda: progress_bar.configure(value=progress['done']))
                            _ui(lambda l=label: progress_label.configure(text=l))
            finally:
                if process is not None:
                    try:
                        process.stdin.close()
                    except Exception:
                        pass
                    try:
                        process.wait()
                    except Exception:
                        pass
                    if not interrupted and process.returncode not in (0, None):
                        print('Video encoder exited with code', process.returncode)
                        encoder_failed = True
                cache_dir = ctx.get('bg_cache_dir')
                if cache_dir:
                    shutil.rmtree(cache_dir, ignore_errors=True)
                if progress_file:
                    try:
                        os.remove(progress_file)
                    except OSError:
                        pass
            if encoder_failed:
                ok = False
                _ui(lambda: progress_label.configure(
                    text='Encoder failed - see console output (is the output file open in another program?).'))
                break
            if interrupted:
                break
    except SystemExit:
        raise
    except Exception:
        ok = False
        traceback.print_exc()
        if progress_file:
            try:
                os.remove(progress_file)
            except OSError:
                pass
        if ctx is not None:
            cache_dir = ctx.get('bg_cache_dir')
            if cache_dir:
                shutil.rmtree(cache_dir, ignore_errors=True)
        if not HEADLESS:
            _ui(lambda: show_error(
                'Render error', 'A problem occurred during rendering.\nSee console output for details.'))
    finally:
        def finish_ui():
            progress_bar.configure(value=0, status='')
            continue_button.configure(text='Render', command=lambda: start_render())
            set_ui_state('normal')
        _ui(finish_ui)

    if interrupted:
        ok = False
        _ui(lambda: progress_label.configure(text='Render was cancelled.'))
    elif ok and not preview:
        total = progress['total']
        if not HEADLESS and last_path:
            def show_output():
                abspath = os.path.abspath(last_path)
                try:
                    subprocess.Popen('explorer /select,"{}"'.format(abspath))
                except Exception:
                    try:
                        subprocess.Popen(['explorer', os.path.dirname(abspath)])
                    except Exception as error:
                        print('Could not open output location:', error)
            _ui(show_output)
        _ui(lambda total=total: progress_label.configure(text=f'Finished - rendered {total} frames'))
    if old_switch is not None:
        try:
            sys.setswitchinterval(old_switch)
        except Exception:
            pass
    return ok


def preview_refresh():
    global _preview_photo, _preview_image, _preview_cache_key, _preview_cache_ctx
    if not _validate('Preview settings invalid'):
        return
    try:
        params = snapshot_values()
        filepath = params['input_file']
        key = _preview_key(params)
        cached = _preview_cache_ctx
        if cached is not None and _preview_cache_key == key:
            ctx = cached
        else:
            if cached is not None and cached.get('bg_cache_dir'):
                shutil.rmtree(cached['bg_cache_dir'], ignore_errors=True)
            ctx = prepare_context(filepath, params, preview=True, interrupt_state={'interrupt': False})
            _preview_cache_key = key
            _preview_cache_ctx = ctx
        frame_no = round(float(params['preview_position'] or 0.0) / 100.0 * (ctx['frame_count'] - 1))
        frame_no = max(0, min(ctx['frame_count'] - 1, frame_no))
        img = draw_frame(ctx, frame_no)
        _preview_image = img
        _preview_photo = pil_to_pixmap(img)
        preview_canvas.configure(image=_preview_photo)
        preview_info_label.configure(text=f'Frame {frame_no}/{ctx["frame_count"] - 1} - {img.size[0]}x{img.size[1]}')
    except Exception:
        traceback.print_exc()
        show_error('Preview error', 'Could not render the preview.\nSee console output for details.')


def preview_save():
    global _preview_image
    if _preview_image is None:
        return
    path = save_filename([DialogFiletypes.png], '/export')
    if not path:
        return
    if not os.path.splitext(path)[1]:
        path += '.png'
    try:
        _preview_image.save(path)
    except OSError as error:
        show_error('Save preview error', 'Could not save the preview image.\n' + str(error))
        return
    if not HEADLESS:
        def show_saved():
            abspath = os.path.abspath(path)
            try:
                subprocess.Popen('explorer /select,"{}"'.format(abspath))
            except Exception as error:
                print('Could not open output location:', error)
        _ui(show_saved)


def schedule_preview_refresh(*_):
    global _preview_after_id
    if _preview_after_id is not None:
        try:
            cancel_scheduled(_preview_after_id)
        except Exception:
            pass
    _preview_after_id = schedule(150, preview_refresh)


def main():
    parser = argparse.ArgumentParser(description='Python-MV audio visualizer.')
    parser.add_argument('--input', help='Input audio file to render.')
    parser.add_argument('--export', help='Output video filename.')
    parser.add_argument('--preset', help='Path to a JSON settings preset.')
    parser.add_argument('--no-ui', '--headless', action='store_true', dest='no_ui', help='Render without the user interface.')
    args = parser.parse_args()

    if args.preset:
        try:
            with open(args.preset, 'r', encoding='utf-8') as preset_file:
                preset = json.load(preset_file)
            if 'log_freq' in preset and 'freq_scale' not in preset:
                preset['freq_scale'] = 'Logarithmic' if preset['log_freq'] else 'Linear'
            begin_bulk_load()
            try:
                for name, value in preset.items():
                    set_variable(name, value)
            finally:
                end_bulk_load()
        except Exception as error:
            print('Failed to load preset:', error)
            sys.exit(1)
    if args.input:
        set_variable('input_file', args.input)
    if args.export:
        set_variable('export_file', args.export)

    if args.no_ui:
        try:
            root.withdraw()
        except Exception:
            pass
        ok = False
        if _validate():
            ok = render(params=snapshot_values())
        sys.exit(0 if ok else 1)

    continue_button.configure(command=lambda: start_render())
    preview_button.configure(command=lambda: start_render(preview=True))
    preview_refresh_button.configure(command=preview_refresh)
    preview_save_button.configure(command=preview_save)
    preview_slider.configure(command=schedule_preview_refresh)
    set_preview_refresh(schedule_preview_refresh)
    schedule(50, _drain_ui)
    launch_ui()


if __name__ == '__main__':
    main()