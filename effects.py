import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

__all__ = ["POST_EFFECTS", "apply_post_effect", "apply_post_effects"]

POST_EFFECTS = (
    "None",
    "Vignette",
    "Scanlines",
    "Grain",
    "Chromatic",
    "Bloom",
    "Letterbox",
    "Pixelate",
    "Duotone",
    "Glitch",
)

def _vignette(rgb, strength):
    h, w = rgb.shape[:2]
    ys = (np.arange(h, dtype=np.float32) - (h - 1) * 0.5) / max((h - 1) * 0.5, 1.0)
    xs = (np.arange(w, dtype=np.float32) - (w - 1) * 0.5) / max((w - 1) * 0.5, 1.0)
    radius = np.sqrt(xs[None, :] ** 2 + ys[:, None] ** 2) / math.sqrt(2.0)
    falloff = np.clip((radius - 0.25) / 0.75, 0.0, 1.0) ** 2
    return rgb * (1.0 - strength * falloff[..., None])

def _scanlines(rgb, strength):
    h = rgb.shape[0]
    rows = np.arange(h)
    mult = np.ones(h, dtype=np.float32)
    mult[rows % 4 == 0] = 1.0 - 0.5 * strength
    mult[rows % 4 == 2] = 1.0 - 0.2 * strength
    return rgb * mult[:, None, None]

def _grain(rgb, strength):
    h, w = rgb.shape[:2]
    rng = np.random.default_rng()
    noise = rng.normal(0.0, 22.0 * strength, size=(h, w, 1)).astype(np.float32)
    return rgb + noise

def _chromatic(rgb, strength):
    shift = max(1, int(round(4.0 * strength)))
    out = rgb.copy()
    out[..., 0] = np.roll(rgb[..., 0], -shift, axis=1)
    out[..., 2] = np.roll(rgb[..., 2], shift, axis=1)
    return out

def _bloom(rgb, strength):
    brightness = rgb.max(axis=2)
    mask = np.clip((brightness - 180.0) / 75.0, 0.0, 1.0)
    if not np.any(mask):
        return rgb
    bright = np.clip(rgb * mask[..., None], 0.0, 255.0).astype(np.uint8)
    radius = 1.0 + 7.0 * strength
    blurred = np.asarray(
        Image.fromarray(bright).filter(ImageFilter.GaussianBlur(radius)),
        dtype=np.float32,
    )
    screened = 255.0 - (255.0 - rgb) * (255.0 - blurred) / 255.0
    return rgb + (screened - rgb) * strength

def _letterbox(rgb, strength):
    h = rgb.shape[0]
    bar = max(1, int(round(h * 0.12 * strength)))
    out = rgb.copy()
    out[:bar, :, :] = 0.0
    out[h - bar:, :, :] = 0.0
    return out

def _pixelate(rgb, strength):
    h, w = rgb.shape[:2]
    factor = max(1, int(round(1.0 + 23.0 * strength)))
    if factor <= 1:
        return rgb
    img = Image.fromarray(np.clip(rgb, 0.0, 255.0).astype(np.uint8))
    small = img.resize(
        (max(1, w // factor), max(1, h // factor)), Image.Resampling.NEAREST
    )
    return np.asarray(small.resize((w, h), Image.Resampling.NEAREST), dtype=np.float32)

_DUOTONE_DARK = np.array([24.0, 20.0, 64.0], dtype=np.float32)
_DUOTONE_LIGHT = np.array([255.0, 196.0, 110.0], dtype=np.float32)
_LUMA_WEIGHTS = np.array([0.299, 0.587, 0.114], dtype=np.float32)

def _duotone(rgb, strength):
    luma = rgb @ _LUMA_WEIGHTS
    t = np.clip(luma / 255.0, 0.0, 1.0)[..., None]
    ramp = _DUOTONE_DARK + (_DUOTONE_LIGHT - _DUOTONE_DARK) * t
    return rgb + (ramp - rgb) * strength

def _glitch(rgb, strength):
    h = rgb.shape[0]
    rng = np.random.default_rng()
    out = rgb.copy()
    slices = max(1, int(round(3.0 + 9.0 * strength)))
    max_shift = max(1, int(round(2.0 + 10.0 * strength)))
    max_height = max(2, h // 12)
    for _ in range(slices):
        y0 = int(rng.integers(0, h))
        y1 = min(h, y0 + int(rng.integers(1, max_height)))
        shift = int(rng.integers(-max_shift, max_shift + 1))
        if shift == 0:
            continue
        channel = 0 if rng.random() < 0.5 else 2
        out[y0:y1, :, channel] = np.roll(rgb[y0:y1, :, channel], shift, axis=1)
    return out

_EFFECT_FUNCS = {
    "Vignette": _vignette,
    "Scanlines": _scanlines,
    "Grain": _grain,
    "Chromatic": _chromatic,
    "Bloom": _bloom,
    "Letterbox": _letterbox,
    "Pixelate": _pixelate,
    "Duotone": _duotone,
    "Glitch": _glitch,
}

def apply_post_effect(frame, name, strength):
    if frame is None or name not in POST_EFFECTS or name == "None":
        return frame
    if getattr(frame, "mode", None) not in ("RGB", "RGBA"):
        return frame
    try:
        amount = float(strength)
    except (TypeError, ValueError):
        return frame
    if amount <= 0.0:
        return frame
    amount = min(amount, 1.0)

    arr = np.asarray(frame, dtype=np.uint8).astype(np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3] if frame.mode == "RGBA" else None

    rgb = _EFFECT_FUNCS[name](rgb, amount)

    out = np.clip(rgb, 0.0, 255.0).astype(np.uint8)
    if alpha is not None:
        out = np.dstack((out, alpha.astype(np.uint8)))
    return Image.fromarray(out)

def apply_post_effects(frame, params):
    try:
        if params is None:
            return frame
        name = params.get("post_effect")
        if name is None or name not in POST_EFFECTS or name == "None":
            return frame
        raw = params.get("post_effect_strength", 0.5)
        try:
            strength = float(raw)
        except (TypeError, ValueError):
            strength = 0.5
        return apply_post_effect(frame, name, strength)
    except Exception:
        return frame
