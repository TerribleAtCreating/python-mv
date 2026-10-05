# Python-MV

Python-MV is an audio visualizer and music video renderer built in Python with a PySide6 interface. It decodes an audio file with ffmpeg, analyzes the signal with numpy FFTs, draws every frame with Pillow (bars, background, overlays and optional post effects) and pipes the frames into ffmpeg for encoding. Outputs are written to the `export/` folder as MP4, WebM, GIF or a PNG sequence, and complete render setups can be saved as JSON presets in `presets/`.

Current version: 0.5.0 (see `version.txt`).

## Features

- FFT audio analysis with configurable size, overlap, window, frequency scale and band measure.
- Horizontal, Vertical and Radial bar layouts with mirror, exact positioning and drag-on-preview.
- Solid bars with multi-stop gradients for bars and background, plus exact positioning and drag-on-preview.
- Background image or video with darken, blur, zoom, pan and bass-driven blur pulse.
- Overlays (waveform, title, watermark) and post effects (Vignette, Scanlines, Grain, Chromatic, Bloom, Letterbox, Pixelate, Duotone, Glitch).
- Transparent PNG output, beat pulse, and an optional maximum output size.
- Live progress with ETA, estimated size and encoder FPS; unavailable encoders are greyed out with automatic fallback.
- Batch rendering, JSON presets (Turbo, Quick, Vocal, Punchy) and a headless CLI.

## Requirements

- Python 3.10 or newer (developed on Python 3.14).
- Run one of the following commands to install Python packages:
  
  ```
  pip install ffmpeg-python numpy Pillow PySide6
  ```
  ```
  pip install -r requirements.txt
  ```
  Note that some libraries may require additional configuration from the user to proceed with the installation.
- A system **ffmpeg** binary available on `PATH` (`ffmpeg` and `ffprobe`).
- Hardware encoders (NVENC) additionally require a recent GPU driver.

## Quick start

1. Run the app:

   ```
   python visualizer.py
   ```

   On Windows you can also use `start.bat`.
2. Click **Load Preset** and choose one from `presets/` (for example `presets/quick.json`).
3. Pick the input audio file in the Main tab (files placed in `files/` are suggested there).
4. Adjust settings as desired, preview a frame in the Preview tab, then click **Render**.

With **Auto name** enabled, the output is written as `export/export_<audio filename>.<ext>`, for example `export/export_song.mp4`. PNG sequence renders create a numbered folder instead of a single file.

## Command line

Headless rendering:

```
python visualizer.py --no-ui --preset presets/punchy.json --input song.mp3 --export myvideo
```

- `--input` and `--export` override values from the preset and can be omitted when the preset already contains an input file and output name.
- `--preset` is optional as well; without it the default settings are used.
- `--headless` is an alias of `--no-ui`.

## Tabs and settings

### Main

Import/export plus encoding and output:

- **Input audio** / **Batch audio files** with **Input mode** (Single or Batch).
- **Export filename** and **Export name** (Auto name or Manual name).
- **Output format** (MP4, WebM, GIF, PNG sequence) and **Encoder** (Auto or an explicit codec; unavailable encoders are greyed out).
- **Quality (0-100)**: CRF-based quality, 0 = best/largest, 100 = smallest/worst.
- **Encoding speed**: Fastest, Fast, Balanced or Best.
- **Max output size (MB, 0 = Unlimited)**: optional cap that limits the bitrate.
- **Copy audio track**: copy the original audio stream instead of re-encoding.
- **Video upscale**: pre-upscale small background images to the selected resolution.
- **Framerate**, **Resolution width/height** (0 = use the background/canvas size), **Start (s)** and **End (s)** for partial renders.

### Audio

Signal conditioning and spectrum analysis:

- **Channel panning**, **Gain (dB)**, **Normalize audio**, **Bass boost (0-3)** and **Bass crossover (Hz)**.
- **FFT size** (256-16384), **FFT overlap (0-94%)** and **Window function** (Hann, Hamming, Blackman, Bartlett, Rectangular).
- **Frequency scale**, **Minimum/Maximum frequency**, **Noise floor (dB)**, **Dynamic range (dB)**, **Band measure** and **Spectral tilt**.
- **Vocal boost**, **Vocal center** and **Vocal width**.
- **Edge taper**, **Edge taper left/right** and **Edge taper curve** (Smooth, Linear, Sharp).

### Timing

- **Smoothing** with **Attack alpha**, **Decay alpha** and **Fast decay multiplier**.
- **Lookahead offset (s)**: shift the visualization in time; positive = bars respond early.

### Bars

- **Number of bars** (1-64), **Bar layout**, **Bar spacing (px)** and **Mirror**.
- **Coverage width/height**, **Justify X/Y**, **Bar length scale**, **Height exponent**, **Brightness exponent**, **Corner radius**, **Outline width/color**, **Reflection** and **Peak caps**.
- **Bar position**: Auto (uses justification) or Exact (X/Y percentage; draggable on the preview outside Radial mode).
- **Radial mode**: base radius, thickness, start angle, sweep, bar margin and rotation cycles.

### Colors

- **Color style**: Brightness, Solid, Gradient or Rainbow.
- **Gradient colors** (multi-stop) and **Bar color**.
- **Rainbow**: saturation, hue offset and cycles.
- **Glow** (radius, strength) and **Trails** (fade, scale).
- **Background style** (Image, Video, Solid, Gradient), **Solid color**, **Transparent background** and **Background gradient**.

### Effects

- **Background image / video**, **Darken background** and **Background blur**.
- **Background animation**: Zoom, Pan (X, Y, speed) and Blur pulse (amount, response).
- **Post processing**: any post effect with a strength value, plus **Beat pulse** and its strength.
- **Waveform overlay**: toggle, color, opacity, scale, style (Center or Bounce) and window in seconds.
- **Title overlay**: toggle, text, color, size and X/Y position.

### Watermark

- **Toggle watermark**, **Watermark image**, **Watermark size** and **Position X/Y**.
- **Blending mode**: Additive, Additive (unclipped), Subtractive or Subtractive (unclipped).

### Preview

- **Frame position (%)** slider (0 = start, 100 = end).
- **Refresh frame** and **Save preview PNG** buttons.
- A canvas showing the rendered frame and its frame number/resolution.

The bottom bar holds **Save Preset**, **Load Preset**, **Preview**, **Render** and the progress display (percent, ETA, estimated size, encoder FPS and render speed).

## Spectrum guide

- **FFT size**: larger windows resolve low frequencies better but render slower.
- **FFT overlap**: higher overlap gives smoother time resolution (the UI allows up to 94%).
- **Band measure**: Average (RMS energy of the band), Peak (strongest bin) or Single bin (raw FFT, most detail).
- **Frequency scale**: Logarithmic (equal bars per octave), Mel (perceptual, more detail in the mids) or Linear (equal Hz).
- **Spectral tilt**: weighting in dB per octave; +3 to +5 flattens the natural downward slope of music.
- **Dynamic range + noise floor**: the dynamic range spans the bar length, so keep the noise floor at roughly minus the dynamic range so hits can reach full height (for example, a dynamic range of 50 pairs well with a noise floor near -50 dB).
- **Vocal boost**: boosts the vocal presence range (center defaults to 1200 Hz); the width sets how many octaves around the center are affected. Useful for lyric visibility.
- **Edge taper**: fades the low/high ends of the bar profile, with separate left/right fractions and a Smooth, Linear or Sharp curve.
- **Timing offset**: shifts the bars in time; positive values look ahead, negative values lag behind the audio.

> [!TIP]
> For faithful, detailed bars keep **Band measure** on *Single bin* or *Peak* and set **Noise floor** close to the negative of **Dynamic range** so the loudest hits reach full height.

## Presets

| Preset | Purpose |
| --- | --- |
| `quick` | General purpose: 32 bars at 4096-point FFT, Peak measure, teal-to-violet gradient, glow, trails and 60 fps. |
| `punchy` | Maximum dynamics: 64 bars, 16384-point FFT at 93% overlap, Single-bin measure, fast attack, 50 dB range. |
| `vocal` | Lyric visibility: Peak measure with an 8 dB vocal boost at 1.2 kHz and the same detailed FFT settings. |
| `turbo` | Fastest render: Fastest encoding speed, 30 fps, 24 bars and no glow or trails. |

> [!TIP]
> Use **Turbo** for quick drafts, then switch to **Quick**, **Punchy** or **Vocal** for the final render.

## Performance

Rendering is CPU-bound: Pillow frame generation is usually the bottleneck and the encoder waits on it. Measured references from this project:

- 720p60 with effects: about 45 fps frame generation with libx264.
- Turbo preset: about 100 fps.
- A heavy 1080p export was optimized to about 2x realtime.

Tips to speed up renders:

- Set **Encoding speed** to **Fastest**.
- Lower the resolution and/or framerate.
- Disable glow, trails and the blur pulse.
- Start from the `turbo` preset.

NVENC hardware encoders are available when the driver supports them, but for typical bar content they have not been faster than libx264 in this project, because frame generation dominates the render time.

> [!WARNING]
> Rendering is CPU-bound. 4K with glow, trails and the blur pulse enabled can take far longer than real time, so check the ETA before starting a long export.

> [!NOTE]
> Hardware encoders (NVENC) are used only when available; otherwise the encoder stage falls back to libx264 automatically.

## Troubleshooting

- **Hardware encoder unavailable**: the encoder menu greys it out with a tooltip, and the encoder stage falls back to libx264. Update your GPU driver to enable NVENC.
- **Output file locked**: if the render stops with a message about the file being open in another program, close the media player or editor holding it and render again.
- **MP3 cover art**: only the audio stream is decoded and analyzed, so embedded artwork is ignored.
- **Transparent background**: the option only applies to PNG sequence output; video formats always render an opaque background.
- **Audio copy**: only works when the source codec is MP4-compatible (AAC, MP3, AC3, EAC3, ALAC). Otherwise the audio is re-encoded to AAC.

> [!IMPORTANT]
> Close the output file in any media player before re-rendering to the same name; a locked file makes the encoder fail at the end.

## License

See repository for license details.
