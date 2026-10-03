# Settings

This is the complete reference for every setting in Python-MV, grouped by the tab where it appears. The name in backticks is the internal key used in presets, the command line and this document; the bold text is the label shown in the interface. Performance is a rough rating of how much each setting slows a render: N/A, Low, Medium or High.

## Main

### Import & export

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Input audio** | Audio file to visualize. | WAV, MP3, FLAC, M4A, AAC, OGG, Opus, WMA, AIFF, APE, AMR, MIDI and similar; files in files/ are suggested. | N/A |
| **Input mode** | Render one input file or a whole batch. | Batch, Single (default Single). | N/A |
| **Batch audio files** | Files rendered one after another in Batch mode. | One or more audio files. | Low |
| **Export filename** | Output name, without extension. | Text; used when Export name is Manual name. | N/A |
| **Export name** | Automatically name the output after the input file. | Auto name, Manual name (default Manual name). | N/A |

### Encoding & output

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Output format** | Container and codec family for the rendered video. | MP4, WebM, GIF, PNG sequence (default MP4). | Low |
| **Encoder** | Video encoder; unavailable encoders are greyed out. | Auto, libx264 (CPU), h264_nvenc (NVIDIA GPU), libx265 (HEVC, CPU), hevc_nvenc (NVIDIA GPU), libvpx-vp9 (CPU), None; choices depend on the output format (default Auto). | Medium |
| **Quality (0-100)** | CRF-based quality, 0 = smallest/worst, 100 = best/largest. | 0-100 (default 80). | Low |
| **Encoding speed** | Trade quality and file size for encoding speed. | Fastest, Fast, Balanced, Best (default Fast). | Medium |
| **Max output size (MB, 0 = Unlimited)** | Cap the bitrate so the file fits within a target size. | 0 or more MB; 0 = unlimited (default 0). | Low |
| **Copy audio track** | Copy the original audio stream instead of re-encoding it. | Enabled, Disabled (default Disabled; MP4 only). | Low |
| **Video upscale** | Pre-upscale small background images to a target resolution. | No upscale, 720p (SD), 1080p (HD), 1440p (QHD), 2160p (UHD - 4K), 4320p (UHD - 8K) (default No upscale). | Low |
| **Framerate** | Frames rendered per second. | 1 or more (default 30). | High |
| **Resolution width (0 = Automatic)** | Output width in pixels. | 0 = background/canvas size, otherwise pixels (default 0). | High |
| **Resolution height (0 = Automatic)** | Output height in pixels. | 0 = background/canvas size, otherwise pixels (default 0). | High |
| **Start (s)** | Start time for partial renders. | Seconds; 0 = beginning (default 0.0). | N/A |
| **End (s)** | End time for partial renders. | Seconds; 0 = end of file, must be after Start (default 0.0). | N/A |

## Audio

### Input analysis

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Channel panning** | Stereo balance of the signal before analysis. | 0.0-1.0; 0.5 = centered (default 0.5). | N/A |
| **Gain (dB)** | Extra gain applied to the signal in decibels. | dB, positive or negative (default 0). | N/A |
| **Normalize audio** | Normalize loudness so the bars use the full dynamic range. | Enabled, Disabled (default Disabled). | N/A |
| **Bass boost (0-3)** | Bass shelf boost. | 0.0-3.0; 0 = off (default 0.0). | N/A |
| **Bass crossover (Hz)** | Frequency below which the bass boost applies. | Hz (default 150). | N/A |

### Spectrum

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **FFT size** | FFT window size; larger resolves low frequencies better but renders slower. | 256, 512, 1024, 2048, 4096, 8192, 16384 (default 2048). | High |
| **FFT overlap (0-94%)** | Percent overlap between FFT windows; higher is smoother. | 0-94 (default 75). | Medium |
| **Window function** | Window applied before the FFT. | Hann, Hamming, Blackman, Bartlett, Rectangular (default Hann). | N/A |
| **Frequency scale** | Frequency axis spacing. | Logarithmic, Mel, Linear (default Logarithmic). | N/A |
| **Log frequency scale (legacy)** | Fallback used only when the frequency scale is empty; True selects Logarithmic. | True, False (default True). | N/A |
| **Minimum frequency (Hz)** | Lowest frequency shown by the bars. | Hz, 0 or greater (default 20). | N/A |
| **Maximum frequency (Hz)** | Highest frequency shown by the bars. | Hz, greater than the minimum frequency (default 20000). | N/A |
| **Noise floor (dB)** | Decibel level treated as silence. | dB (default -60). | N/A |
| **Dynamic range (dB)** | Dynamic range in dB spanned by the bar length. | dB, greater than 0 (default 50). | N/A |
| **Band measure** | How each bar summarizes its band. | Average, Peak, Single bin (default Average). | Low |
| **Spectral tilt (dB/oct)** | dB per octave weighting; positive values lift high frequencies. | dB/oct (default 0.0). | N/A |
| **Vocal boost (dB)** | Boost of the vocal presence range. | dB; 0 = off (default 0.0). | N/A |
| **Vocal center (Hz)** | Center frequency of the vocal boost. | Hz (default 1200.0). | N/A |
| **Vocal width (oct)** | Width of the vocal boost in octaves. | Octaves, greater than 0 (default 1.6). | N/A |
| **Edge taper (0-1)** | Fade the far edges of the bar profile. | 0.0-1.0; 0 = off (default 0.0). | N/A |
| **Edge taper left** | Low-end fraction that is faded. | 0.0-0.5 (default 0.25). | N/A |
| **Edge taper right** | High-end fraction that is faded. | 0.0-0.5 (default 0.25). | N/A |
| **Edge taper curve** | Shape of the edge fade. | Smooth, Linear, Sharp (default Smooth). | N/A |

> [!TIP]
> Keep **Noise floor** close to the negative of **Dynamic range** so the loudest bars reach full height without pinning.

## Timing

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Smoothing** | Enable attack/decay smoothing so bars move smoothly. | Enabled, Disabled (default Enabled). | N/A |
| **Attack alpha** | Fraction of the gap a bar closes each frame while rising; 1 = instant. | 0.0-1.0 (default 0.5). | N/A |
| **Decay alpha** | Fraction of the gap a bar closes each frame while falling. | 0.0-1.0 (default 0.12). | N/A |
| **Fast decay multiplier** | Extra decay speed applied after a large drop. | 1.0 or more (default 1.8). | N/A |
| **Lookahead offset (s)** | Shift the visualization in time; positive = bars respond early. | Seconds, positive or negative (default 0.0). | N/A |

## Bars

### Bar layout

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Number of bars** | Number of frequency bars rendered. | 1-64 (default 25). | Medium |
| **Bar layout** | Orientation of the bars. | Horizontal, Vertical, Radial (default Horizontal). | Low |
| **Bar spacing (px)** | Gap between individual bars. | Pixels (default 5). | N/A |
| **Mirror** | Mirror the bars around the anchor line. | Mirrored, Not mirrored (default Not mirrored). | Low |

### Sizing & shaping

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Coverage width** | Fraction of the width the bars span. | 0.0-1.0; 1.0 = full width (default 1.0). | N/A |
| **Coverage height** | Fraction of the height the bars span. | 0.0-1.0 (default 0.5). | N/A |
| **Justify X** | Horizontal justification. | 0.0-1.0; 0 = left, 1 = right (default 0.5). | N/A |
| **Justify Y** | Vertical justification. | 0.0-1.0; 0 = top, 1 = bottom (default 1.0). | N/A |
| **Bar length scale** | Global multiplier for bar length. | Multiplier (default 1.0). | N/A |
| **Height exponent** | Exponent on bar height; 1 = linear, below 1 lifts quiet bands. | Exponent (default 1.0). | N/A |
| **Brightness exponent** | Exponent on bar brightness; below 1 makes small bars brighter. | Exponent (default 0.0). | N/A |
| **Corner radius (px)** | Rounded-corner radius of each bar. | Pixels (default 0). | Low |
| **Outline width (px)** | Bar outline width. | Pixels; 0 = no outline (default 0). | Low |
| **Outline color** | Color of the bar outline. | Hex color (default #000000). | N/A |
| **Reflection** | Draw a fading reflection beneath the bars. | Enabled, Disabled (default Disabled). | Medium |
| **Reflection strength** | Opacity of the bar reflection. | 0.0-1.0 (default 0.35). | Medium |
| **Peak caps** | Draw a cap marker at each band peak. | Enabled, Disabled (default Disabled). | Low |
| **Peak cap height (px)** | Thickness of the peak cap marker. | Pixels, 1 or more (default 6). | N/A |

### Bar position

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Position mode** | Auto uses justification; Exact uses the percentages below. | Auto, Exact (default Auto). | N/A |
| **Position X (%)** | Exact horizontal anchor. | 0-100 (default 50.0). | N/A |
| **Position Y (%)** | Exact vertical anchor. | 0-100 (default 50.0). | N/A |

### Radial mode

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Base radius** | Inner radius of the radial bars. | 0.0-1.0 relative to the canvas (default 0.2). | N/A |
| **Thickness** | Thickness of the radial bars. | Relative value (default 0.5). | N/A |
| **Start angle (deg)** | Start angle of the radial arrangement. | Degrees (default 270). | N/A |
| **Sweep (deg)** | Angular sweep of the radial bars; 360 = full circle. | Degrees (default 360). | N/A |
| **Bar margin (deg)** | Angular gap between radial bars. | Degrees (default 2). | N/A |
| **Rotation cycles** | Rotation applied across the radial bars. | Cycles (default 0.0). | N/A |

## Colors

### Bar coloring

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Color style** | How bar colors are chosen. | Brightness, Solid, Gradient, Rainbow (default Brightness). | N/A |
| **Gradient colors** | Multi-stop gradient for the bars. | List of position/hex color stops (default white to #00ccff). | N/A |
| **Bar color** | Base color for Solid; first stop of the gradient ramp. | Hex color (default #ffffff). | N/A |
| **Gradient end color** | Last stop of the gradient ramp. | Hex color (default #00ccff). | N/A |

### Rainbow

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Saturation** | Saturation of rainbow colors. | 0.0-1.0; 0 = gray, 1 = vivid (default 1.0). | N/A |
| **Hue offset (deg)** | Global hue offset of the rainbow. | Degrees (default 0). | N/A |
| **Cycles** | How many times the rainbow cycles across the bars. | 1 or more (default 1). | N/A |

### Glow & trails

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Glow effect** | Add a soft glow behind the bars. | Enabled, Disabled (default Disabled). | High |
| **Glow radius (px)** | Blur radius of the glow. | Pixels (default 10). | High |
| **Glow strength** | Intensity of the glow. | 0.0-1.0 (default 0.6). | Medium |
| **Trails** | Draw a faded ghost of each bar at its recent peak. | Enabled, Disabled (default Disabled). | Medium |
| **Trail fade** | Opacity of the trail ghost. | 0.0-1.0 (default 0.3). | Medium |
| **Trail scale** | Height the trail ghost follows. | Multiplier (default 0.8). | N/A |

### Background colors

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Background style** | Background rendering source. | Image, Video, Solid, Gradient (default Solid). | Low |
| **Solid color** | Color used by the Solid background style. | Hex color (default #000000). | N/A |
| **Transparent background** | Render a transparent background. | Transparent, Opaque (default Opaque; PNG sequence only). | Low |
| **Background gradient** | Multi-stop gradient for the background. | List of position/hex color stops (default #101026 to #20204a). | N/A |
| **Gradient start color** | Fallback first color of the background gradient. | Hex color (default #101026). | N/A |
| **Gradient end color** | Fallback last color of the background gradient. | Hex color (default #20204a). | N/A |

## Effects

### Background

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Background image / video** | File used by the Image and Video background styles. | PNG/JPG image or MP4/WebM/GIF/MOV video. | Low |
| **Darken background (0-1)** | Darken the background so the bars stand out. | 0.0-1.0; 0 = unchanged, 1 = black (default 0.0). | Low |
| **Background blur (px)** | Constant background blur. | Pixels; 0 = off (default 0). | Medium |

### Background animation

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Zoom** | Slowly zoom the background in and out over time. | Enabled, Disabled (default Disabled). | Medium |
| **Zoom amount** | Strength of the background zoom. | Fraction (default 0.08). | Medium |
| **Zoom cycles** | Number of zoom cycles over the video. | Cycles (default 1.0). | N/A |
| **Pan** | Slowly pan the background across the canvas. | Enabled, Disabled (default Disabled). | Medium |
| **Pan X** | Horizontal travel for the pan. | Fraction of the image (default 0.3). | N/A |
| **Pan Y** | Vertical travel for the pan. | Fraction of the image (default 0.15). | N/A |
| **Pan speed** | Speed of the background panning. | Multiplier (default 0.5). | N/A |
| **Blur pulse** | Pulse the background blur with the bass. | Enabled, Disabled (default Disabled). | High |
| **Blur amount (px)** | Maximum blur radius reached at the strongest bass hit. | 0-50 px (default 12). | High |
| **Blur response** | How strongly bass energy drives the pulse. | Multiplier (default 1.0). | Medium |

### Post processing

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Post effect** | Full-frame effect applied after everything else. | None, Vignette, Scanlines, Grain, Chromatic, Bloom, Letterbox, Pixelate, Duotone, Glitch (default None). | Medium |
| **Post effect strength** | Intensity of the post effect. | 0.0-1.0 (default 0.5). | Medium |
| **Beat pulse** | Pulse the visuals in time with detected beats. | Enabled, Disabled (default Disabled). | Medium |
| **Beat pulse strength** | Intensity of the beat pulse. | 0.0-1.0 (default 0.5). | Low |

### Waveform overlay

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Show waveform** | Overlay the audio waveform on the canvas. | Enabled, Disabled (default Disabled). | Medium |
| **Waveform color** | Color of the waveform overlay. | Hex color (default #00ff88). | N/A |
| **Waveform opacity** | Opacity of the waveform overlay. | 0.0-1.0 (default 0.6). | N/A |
| **Waveform scale** | Vertical scale of the waveform. | Multiplier (default 0.8). | N/A |
| **Waveform style** | Center draws around the middle; Bounce grows from the bottom. | Center, Bounce (default Center). | N/A |
| **Waveform window (s)** | Seconds of audio shown in the waveform window. | Seconds (default 2.0). | N/A |

### Title overlay

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Show title** | Overlay text on the video. | Enabled, Disabled (default Disabled). | Low |
| **Title text** | Text to draw on the video. | Text (default empty). | N/A |
| **Title color** | Color of the title text. | Hex color (default #ffffff). | N/A |
| **Title size** | Font size of the title text. | Pixels (default 48). | N/A |
| **Title X** | Horizontal title position. | 0.0-1.0; 0 = left, 1 = right (default 0.5). | N/A |
| **Title Y** | Vertical title position. | 0.0-1.0; 0 = top, 1 = bottom (default 0.08). | N/A |

## Watermark

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Toggle watermark** | Overlay a watermark image on the video. | Enabled, Disabled (default Disabled). | Low |
| **Watermark image** | Watermark image file. | PNG, JPG or GIF image. | N/A |
| **Watermark size (0-1)** | Size relative to the smaller canvas dimension. | 0.0-1.0 (default 0.5). | N/A |
| **Blending mode** | Blend mode used to combine the watermark with the frame. | Additive, Additive (unclipped), Subtractive, Subtractive (unclipped) (default Additive). | Low |
| **Position X** | Horizontal watermark position. | 0.0-1.0; 0 = left, 1 = right (default 0.5). | N/A |
| **Position Y** | Vertical watermark position. | 0.0-1.0; 0 = top, 1 = bottom (default 0.5). | N/A |

## Preview

| Setting | Description | Range / Options | Performance |
| --- | --- | --- | --- |
| **Frame position (%)** | Which frame of the audio to show in the preview. | 0-100; 0 = start, 100 = end (default 0). | N/A |

The Refresh frame and Save preview PNG buttons on this tab have no settings of their own.

## Presets

- `turbo`: fastest render; Fastest encoding speed, 30 fps, 24 bars and no glow or trails.
- `quick`: general purpose; 32 bars at 4096-point FFT, Peak measure, teal-to-violet gradient, glow, trails and 60 fps.
- `vocal`: lyric visibility; Peak measure with an 8 dB vocal boost at 1.2 kHz and detailed 16384-point FFT settings.
- `punchy`: maximum dynamics; 64 bars, 16384-point FFT at 93% overlap, Single-bin measure, fast attack and a 50 dB range.

See [README.md](README.md) for setup and usage.
