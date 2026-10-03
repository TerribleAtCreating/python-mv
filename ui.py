from import_modules import *
from resources import *

try:
    import effects as _effects
    POST_EFFECT_NAMES = list(_effects.POST_EFFECTS)
except Exception:
    POST_EFFECT_NAMES = ['None']

currentVersion = "0.5.0"
versionStatus = ", indev"
app_id = 'terriac.pythonmv.main.050'

# ------------------------------------------------------------------ palette
BG = '#171310'
PANEL = '#1e1a16'
PANEL2 = '#282219'
FIELD = '#2c261d'
BORDER = '#41382b'
FG = '#ede8df'
MUTED = '#a79d8a'
ACCENT = '#df9442'
ACCENT2 = '#eba559'
DANGER = '#d4584a'
DISABLED_FG = '#6e6656'
FONT_FAMILY = 'Segoe UI'

Qt = QtCore.Qt

app = QtWidgets.QApplication([])
QtWidgets.QApplication.setStyle('Fusion')
app.setApplicationName('Python-MV')
app.setApplicationDisplayName('Python-MV [' + currentVersion + versionStatus + ']')
app.setApplicationVersion(currentVersion)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
try:
    app.setWindowIcon(QtGui.QIcon('pymv.png'))
except Exception:
    pass

APP_FONT = QtGui.QFont(FONT_FAMILY, 9)
app.setFont(APP_FONT)

_palette = app.palette()
_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(BG))
_palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(FG))
_palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(FIELD))
_palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(PANEL2))
_palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor('#23262d'))
_palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(FG))
_palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(FG))
_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(FIELD))
_palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(FG))
_palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor('#ff0000'))
_palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(ACCENT))
_palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor('#191206'))
_palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, QtGui.QColor(MUTED))
_palette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, QtGui.QColor(DISABLED_FG))
_palette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(DISABLED_FG))
app.setPalette(_palette)

QSS = """
* { outline: none; }
QWidget { font-family: "Segoe UI"; font-size: 9pt; color: %(fg)s; }
#RootPanel { background: %(bg)s; border: 1px solid %(border)s; border-radius: 6px; }

QTabWidget::pane { border: none; background: %(panel)s; }
QTabWidget::tab-bar { alignment: left; }
QTabBar { background: %(bg)s; }
QTabBar::tab { background: transparent; color: %(muted)s; padding: 9px 15px; margin-right: 1px;
    border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom: 2px solid transparent; }
QTabBar::tab:hover { background: %(panel2)s; color: %(fg)s; }
QTabBar::tab:selected { color: %(fg)s; border-bottom: 2px solid %(accent)s; }

QLabel { background: transparent; color: %(fg)s; }
QLabel#Section { color: %(muted)s; font-size: 8pt; font-weight: 700; letter-spacing: 1px; padding: 14px 0 2px 2px; }
QLabel#FieldLabel { color: %(fg)s; }
QLabel#Muted { color: %(muted)s; }
QLabel#Status { color: %(muted)s; font-size: 8pt; }
QFrame#HLine { background: %(border)s; max-height: 1px; min-height: 1px; }

QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #3a332a; border-radius: 3px; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: #4a4134; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: #3a332a; border-radius: 3px; min-width: 28px; }
QScrollBar::handle:horizontal:hover { background: #4a4134; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QLineEdit { background: %(field)s; border: 1px solid %(border)s; border-radius: 3px; padding: 5px 9px; selection-background-color: %(accent)s; selection-color: #191206; }
QLineEdit:hover { border-color: #4a4134; }
QLineEdit:focus { border-color: %(accent)s; }
QLineEdit[invalid="true"] { border-color: %(danger)s; }
QLineEdit:disabled { color: %(disabled_fg)s; background: #201b15; }
QLineEdit#FileEnt { background: %(field)s; }
QLineEdit#FileEnt[invalid="true"] { border-color: %(danger)s; }

QPushButton { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s; border-radius: 4px;
    padding: 6px 14px; font-weight: 500; }
QPushButton:hover { background: %(panel2)s; border-color: #4a4134; }
QPushButton:pressed { background: #383025; }
QPushButton:disabled { color: %(disabled_fg)s; background: #201b15; border-color: #2b2620; }
QPushButton#Accent { background: %(accent)s; color: #191206; border: 1px solid %(accent)s; font-weight: 700; padding: 7px 18px; }
QPushButton#Accent:hover { background: %(accent2)s; border-color: %(accent2)s; }
QPushButton#Accent:pressed { background: #c9812f; }
QPushButton#Accent:disabled { background: #42382a; color: #94876a; border-color: #42382a; }
QPushButton#Ghost { background: transparent; border: 1px solid %(border)s; color: %(muted)s; }
QPushButton#Ghost:hover { background: %(panel2)s; color: %(fg)s; border-color: #4a4134; }
QPushButton#Ghost:disabled { color: %(disabled_fg)s; background: transparent; }

QComboBox { background: %(field)s; border: 1px solid %(border)s; border-radius: 3px; padding: 5px 26px 5px 9px; min-height: 16px; }
QComboBox:hover { border-color: #4a4134; }
QComboBox:focus { border-color: %(accent)s; }
QComboBox:disabled { color: %(disabled_fg)s; background: #201b15; }
QComboBox::drop-down { border: none; width: 20px; subcontrol-origin: padding; subcontrol-position: center right; }
QComboBox QAbstractItemView { background: %(field)s; border: 1px solid #4a4134; border-radius: 5px;
    selection-background-color: %(accent)s; selection-color: #191206; padding: 3px; outline: none; }
QComboBox QAbstractItemView::item { min-height: 23px; padding: 3px 9px; border-radius: 3px; }
QComboBox QAbstractItemView::item:hover { background: #3a332a; color: %(fg)s; }

QProgressBar { background: %(field)s; border: 1px solid %(border)s; border-radius: 3px; min-height: 20px; max-height: 20px;
    text-align: center; color: %(fg)s; font-size: 8pt; }
QProgressBar::chunk { background: %(accent)s; border-radius: 2px; }

QSlider::groove:horizontal { height: 5px; border-radius: 2px; background: %(field)s; }
QSlider::sub-page:horizontal { height: 5px; border-radius: 2px; background: %(accent)s; }
QSlider::handle:horizontal { width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;
    background: %(fg)s; border: 1px solid %(border)s; }
QSlider::handle:horizontal:hover { background: #ffffff; border-color: %(accent)s; }
QSlider:disabled { color: %(disabled_fg)s; }

QToolTip { background-color: #241f18; color: %(fg)s; border: 1px solid #4a4134; border-radius: 4px; padding: 5px 8px; }

QLabel#PreviewCanvas { background: #0f0c08; border: 1px solid %(border)s; border-radius: 6px; }
""" % {
    'fg': FG, 'bg': BG, 'panel': PANEL, 'panel2': PANEL2, 'field': FIELD, 'border': BORDER,
    'accent': ACCENT, 'accent2': ACCENT2, 'muted': MUTED, 'danger': DANGER, 'disabled_fg': DISABLED_FG
}
app.setStyleSheet(QSS)

# ------------------------------------------------------------------ variables
session_variables = {
    'input_file': UserVar(''), 'batch_files': UserVar(''), 'batch_mode': UserVar(False),
    'export_file': UserVar(''), 'export_auto': UserVar(False), 'preview_position': UserVar(0)
}

preset_variables = {}
for _name in [
    'output_format', 'encoder', 'encoder_speed', 'quality', 'max_output_size', 'audio_copy',
    'video_upscale', 'framerate', 'resolution_width', 'resolution_height',
    'audio_start', 'audio_end',
    'channel_pan', 'gain_db', 'normalize', 'bass_boost', 'bass_crossover',
    'fft_size', 'fft_overlap', 'fft_window', 'freq_scale', 'log_freq',     'freq_min', 'freq_max', 'noise_floor', 'db_range', 'band_measure', 'spectral_tilt', 'timing_offset',
    'vocal_boost', 'vocal_center', 'vocal_width',
    'edge_taper', 'edge_taper_left', 'edge_taper_right', 'edge_taper_curve',
    'smoothing_enabled', 'attack_alpha', 'decay_alpha', 'decay_fast',
    'bars', 'bar_layout', 'bar_spacing', 'coverage_x', 'coverage_y',
    'bar_justify_x', 'bar_justify_y', 'mirror', 'bar_scale', 'height_exp', 'brightness_exp',
    'corner_radius', 'outline_width', 'outline_color',
    'bar_peak_caps', 'bar_peak_size',
    'bar_position_mode', 'bar_position_x', 'bar_position_y',
    'bar_reflection', 'reflection_strength',
    'radial_radius', 'radial_thickness', 'radial_start', 'radial_sweep', 'radial_margin', 'radial_rotation',
    'color_style', 'color_a', 'color_b', 'color_stops',
    'rainbow_saturation', 'rainbow_hue', 'rainbow_cycles',
    'effect_glow', 'glow_radius', 'glow_strength', 'effect_trails', 'trail_alpha', 'trail_scale',
    'background', 'bg_style', 'bg_solid_color', 'bg_grad_a', 'bg_grad_b', 'bg_stops', 'bg_transparent', 'bg_darken', 'bg_blur',
    'bg_zoom', 'bg_zoom_amount', 'bg_zoom_cycles', 'bg_pan', 'bg_pan_x', 'bg_pan_y', 'bg_pan_speed',
    'bg_blur_pulse', 'bg_blur_amount', 'bg_blur_response',
    'waveform_toggle', 'waveform_color', 'waveform_opacity', 'waveform_scale', 'waveform_style', 'waveform_window',
    'title_toggle', 'title_text', 'title_color', 'title_size', 'title_x', 'title_y',
    'watermark_toggle', 'watermark_file', 'watermark_size', 'watermark_blending', 'watermark_x', 'watermark_y',
    'post_effect', 'post_effect_strength', 'beat_pulse', 'beat_pulse_strength'
]:
    preset_variables[_name] = UserVar()

default_values = {
    'output_format': 'MP4', 'encoder': 'Auto', 'encoder_speed': 'Fast', 'quality': 80, 'max_output_size': 0, 'audio_copy': False,
    'video_upscale': 'No upscale', 'framerate': 30, 'resolution_width': 0, 'resolution_height': 0,
    'audio_start': 0.0, 'audio_end': 0.0,
    'channel_pan': 0.5, 'gain_db': 0, 'normalize': False, 'bass_boost': 0.0, 'bass_crossover': 150,
    'fft_size': 2048, 'fft_overlap': 75, 'fft_window': 'Hann', 'freq_scale': 'Logarithmic', 'log_freq': True,
    'freq_min': 20, 'freq_max': 20000, 'noise_floor': -60, 'db_range': 50,
    'band_measure': 'Average', 'spectral_tilt': 0.0, 'timing_offset': 0.0,
    'vocal_boost': 0.0, 'vocal_center': 1200.0, 'vocal_width': 1.6,
    'edge_taper': 0.0, 'edge_taper_left': 0.25, 'edge_taper_right': 0.25, 'edge_taper_curve': 'Smooth',
    'smoothing_enabled': True, 'attack_alpha': 0.5, 'decay_alpha': 0.12, 'decay_fast': 1.8,
    'bars': 25, 'bar_layout': 'Horizontal', 'bar_spacing': 5,
    'coverage_x': 1.0, 'coverage_y': 0.5, 'bar_justify_x': 0.5, 'bar_justify_y': 1.0,
    'mirror': False, 'bar_scale': 1.0, 'height_exp': 1.0, 'brightness_exp': 0.0,
    'corner_radius': 0, 'outline_width': 0, 'outline_color': '#000000',
    'bar_peak_caps': False, 'bar_peak_size': 6,
    'bar_position_mode': 'Auto', 'bar_position_x': 50.0, 'bar_position_y': 50.0,
    'bar_reflection': False, 'reflection_strength': 0.35,
    'radial_radius': 0.2, 'radial_thickness': 0.5, 'radial_start': 270, 'radial_sweep': 360,
    'radial_margin': 2, 'radial_rotation': 0.0,
    'color_style': 'Brightness', 'color_a': '#ffffff', 'color_b': '#00ccff',
    'color_stops': '[[0.0, "#ffffff"], [1.0, "#00ccff"]]',
    'rainbow_saturation': 1.0, 'rainbow_hue': 0, 'rainbow_cycles': 1,
    'effect_glow': False, 'glow_radius': 10, 'glow_strength': 0.6,
    'effect_trails': False, 'trail_alpha': 0.3, 'trail_scale': 0.8,
    'background': '', 'bg_style': 'Solid', 'bg_solid_color': '#000000', 'bg_darken': 0.0, 'bg_blur': 0,
    'bg_grad_a': '#101026', 'bg_grad_b': '#20204a',
    'bg_stops': '[[0.0, "#101026"], [1.0, "#20204a"]]', 'bg_transparent': False,
    'bg_zoom': False, 'bg_zoom_amount': 0.08, 'bg_zoom_cycles': 1.0,
    'bg_pan': False, 'bg_pan_x': 0.3, 'bg_pan_y': 0.15, 'bg_pan_speed': 0.5,
    'bg_blur_pulse': False, 'bg_blur_amount': 12, 'bg_blur_response': 1.0,
    'waveform_toggle': False, 'waveform_color': '#00ff88', 'waveform_opacity': 0.6,
    'waveform_scale': 0.8, 'waveform_style': 'Center', 'waveform_window': 2.0,
    'title_toggle': False, 'title_text': '', 'title_color': '#ffffff', 'title_size': 48,
    'title_x': 0.5, 'title_y': 0.08,
    'watermark_toggle': False, 'watermark_file': '', 'watermark_size': 0.5,
    'watermark_blending': 'Additive', 'watermark_x': 0.5, 'watermark_y': 0.5,
    'post_effect': 'None', 'post_effect_strength': 0.5,
    'beat_pulse': False, 'beat_pulse_strength': 0.5
}

for _name, _value in default_values.items():
    if _name in session_variables:
        session_variables[_name].set(_value)
    if _name in preset_variables:
        preset_variables[_name].set(_value)

all_variable_names = list(preset_variables.keys())

# ------------------------------------------------------------------ option help (hover tooltips)
OPTION_HELP = {
    'input_file': 'Input audio file to visualize. Supports WAV, MP3, FLAC, M4A, AAC, OGG, Opus, WMA, AIFF, APE, AMR, MIDI and more.',
    'batch_files': 'Render multiple audio files in one go. Each file gets its own output video.',
    'batch_mode': 'When enabled, all files listed above are rendered. Disabled renders only the single input file.',
    'export_file': 'Output filename (without extension). The format extension is added automatically.',
    'export_auto': "Automatically name output files after the input file instead of using a custom name.",
    'preview_position': 'Which frame of the audio to show in the preview. 0% is the start, 100% is the end.',
    'output_format': 'Container and codec family for the rendered video.',
    'encoder': 'Video encoder. Choose Auto for a sensible default, or pick CPU/GPU encoders directly.',
    'quality': 'CRF-based quality from 0 (smallest/worst) to 100 (best/largest).',
    'encoder_speed': 'Trade quality and file size for encoding speed (Fastest is quickest, Best is slowest).',
    'max_output_size': 'Optional maximum output file size in MB (0 = unlimited). Quality is kept, but the bitrate is capped to fit within this size.',
    'audio_copy': 'Copy the original audio stream instead of re-encoding it. Fast, but the container must support it.',
    'video_upscale': 'Automatically upscale small background images to a target resolution.',
    'framerate': 'Frames rendered per second. Higher = smoother but slower renders.',
    'resolution_width': 'Output width in pixels. 0 = use the background/canvas size.',
    'resolution_height': 'Output height in pixels. 0 = use the background/canvas size.',
    'audio_start': 'Start time in seconds (offset). Use 0 to render from the beginning.',
    'audio_end': 'End time in seconds. Use 0 to render until the end of the file.',
    'channel_pan': 'Stereo balance of the derived signal. 0.5 = centered, 0 = left only, 1 = right only.',
    'gain_db': 'Extra gain applied to the signal in decibels before analysis.',
    'normalize': 'Normalize the signal loudness so bars make full use of the dynamic range.',
    'bass_boost': 'Bass shelf boost from 0 (off) to 3 (maximum).',
    'bass_crossover': 'Crossover frequency (Hz) below which the bass boost is applied.',
    'fft_size': 'FFT window size. Larger values = better low-frequency resolution but slower renders.',
    'fft_overlap': 'Percent overlap between FFT windows. Higher = smoother time resolution.',
    'fft_window': 'Window function used before the FFT. Affects spectral leakage and bar smoothness.',
    'log_freq': 'Use a logarithmic frequency scale (more musically accurate) instead of linear.',
    'freq_scale': 'Frequency axis spacing: Logarithmic (equal bars per octave), Mel (perceptual, more detail in the mids), or Linear (equal Hz).',
    'freq_min': 'Lowest frequency shown by the bars.',
    'freq_max': 'Highest frequency shown by the bars.',
    'noise_floor': 'Decibel level treated as silence. Signals below this map to a zero-length bar.',
    'db_range': 'Dynamic range in dB spanned by the bar length.',
    'band_measure': 'How each bar summarizes its band: Average (RMS energy), Peak (strongest bin), or Single bin (raw FFT - no averaging, most detail).',
    'spectral_tilt': 'Spectral weighting in dB per octave. Positive values lift higher frequencies to compensate the natural downward slope of music (+3 to +5 flattens the profile, like pink weighting).',
    'vocal_boost': 'Boost the vocal presence range so lyrics stand out (dB at the center frequency, 0 = off).',
    'vocal_center': 'Center frequency of the vocal boost in Hz (default 1200 Hz covers most vocals).',
    'vocal_width': 'Width of the vocal boost in octaves (larger = wider band around the center).',
    'timing_offset': 'Shift the visualization in time relative to the audio, in seconds. Positive = bars respond early (lookahead), negative = bars lag.',
    'edge_taper': 'Fade the bars at the far edges so the profile starts and ends lower (0 = off, 1 = full fade).',
    'edge_taper_left': 'How much of the low end is faded, as a fraction of the bars.',
    'edge_taper_right': 'How much of the high end is faded, as a fraction of the bars.',
    'edge_taper_curve': 'Shape of the edge fade: Smooth, Linear or Sharp.',
    'smoothing_enabled': 'Enable attack/decay smoothing so bars fall and rise smoothly.',
    'attack_alpha': 'Fraction of the gap a bar closes each frame while rising (at 60 fps). 1 = instant.',
    'decay_alpha': 'Fraction of the gap a bar closes each frame while falling (at 60 fps). Lower = longer tails.',
    'decay_fast': 'Speed multiplier applied to decay after a large drop. 1 = same as normal decay.',
    'bars': 'Number of frequency bars rendered (1-64).',
    'bar_layout': 'Orientation of the bars: horizontal, vertical or radial (circular).',
    'bar_spacing': 'Gap in pixels between individual bars.',
    'coverage_x': 'Fraction of the width the bars span. 1.0 = full width.',
    'coverage_y': 'Fraction of the height the bars span. 1.0 = full height.',
    'bar_justify_x': 'Horizontal justification. 0 = left, 0.5 = center, 1 = right.',
    'bar_justify_y': 'Vertical justification. 0 = top, 1 = bottom.',
    'mirror': 'Mirror the bars around the anchor line for a symmetric look.',
    'bar_scale': 'Global multiplier for bar length.',
    'height_exp': 'Exponent applied to bar height. 1 = linear (faithful to the audio), <1 lifts quiet bands, >1 boosts peaks.',
    'brightness_exp': 'Exponent applied to bar brightness. <1 makes small bars brighter.',
    'corner_radius': 'Rounded-corner radius of each bar in pixels.',
    'outline_width': 'Outline width of each bar in pixels. 0 = no outline.',
    'outline_color': 'Color of the bar outline.',
    'bar_peak_caps': 'Draw a crisp cap marker at each band peak that falls as the level drops.',
    'bar_peak_size': 'Thickness of the peak cap marker in pixels.',
    'bar_position_mode': 'Auto uses the justify sliders. Exact positions the bars at the X/Y coordinates below.',
    'bar_position_x': 'Exact horizontal anchor of the bars, as a percentage of the canvas width (0-100).',
    'bar_position_y': 'Exact vertical anchor of the bars, as a percentage of the canvas height (0-100).',
    'bar_reflection': 'Draw a fading reflection beneath (or beside) the bars.',
    'reflection_strength': 'Opacity of the bar reflection.',
    'radial_radius': 'Inner radius of the radial bars, relative to the canvas.',
    'radial_thickness': 'Thickness of the radial bars, relative to the canvas.',
    'radial_start': 'Start angle of the radial arrangement, in degrees.',
    'radial_sweep': 'Angular sweep of the radial bars, in degrees. 360 = full circle.',
    'radial_margin': 'Angular gap in degrees between radial bars.',
    'radial_rotation': 'Rotation cycles applied across the radial bars (0-1).',
    'color_style': 'Brightness: color follows the level. Solid: one flat color. Gradient: colors spread across the bars. Rainbow: hue cycle across the bars.',
    'color_a': 'Base color for Solid; also the first stop of the gradient ramp.',
    'color_b': 'Last stop of the gradient ramp (used by Brightness and Gradient).',
    'color_stops': 'Gradient stops for the bars. Double-click the bar to add a stop, double-click a stop to change its color.',
    'rainbow_saturation': 'Saturation of rainbow colors, from 0 (gray) to 1 (vivid).',
    'rainbow_hue': 'Global hue offset of the rainbow, in degrees.',
    'rainbow_cycles': 'How many times the rainbow cycles across the bars.',
    'effect_glow': 'Add a soft glow behind the bars.',
    'glow_radius': 'Blur radius of the glow effect in pixels.',
    'glow_strength': 'Intensity of the glow effect.',
    'effect_trails': 'Draw a faded ghost of each bar at its recent peak, leaving motion trails.',
    'trail_alpha': 'Opacity of the trail ghost (higher = more visible afterimage).',
    'trail_scale': 'How tall the trail ghost follows the peak (1.0 = exactly at the peak).',
    'background': 'Background image. Required when background style is set to Image.',
    'bg_style': 'Background rendering: image, solid color, or a two-color gradient.',
    'bg_solid_color': 'Solid color used when background style is Solid.',
    'bg_grad_a': 'Start color of the background gradient.',
    'bg_grad_b': 'End color of the background gradient.',
    'bg_stops': 'Gradient stops for the background.',
    'bg_transparent': 'Render the background transparent (PNG sequence only).',
    'bg_darken': 'Darken the background so the bars stand out (0 = unchanged, 1 = black).',
    'bg_blur': 'Constant background blur in pixels (separate from the bass blur pulse).',
    'bg_zoom': 'Slowly zoom the background in and out over time.',
    'bg_zoom_amount': 'Strength of the background zoom effect.',
    'bg_zoom_cycles': 'Number of zoom cycles over the video duration.',
    'bg_pan': 'Slowly pan the background across the canvas.',
    'bg_pan_x': 'Horizontal travel (fraction of the image) for the pan effect.',
    'bg_pan_y': 'Vertical travel (fraction of the image) for the pan effect.',
    'bg_pan_speed': 'Speed of the background panning.',
    'bg_blur_pulse': 'Pulse the background blur with the bass so the backdrop goes in and out of focus on each beat.',
    'bg_blur_amount': 'Maximum blur radius reached at the strongest bass hit (0-50 px).',
    'bg_blur_response': 'How strongly the bass energy drives the pulse blur.',
    'waveform_toggle': 'Overlay the audio waveform on the canvas.',
    'waveform_color': 'Color of the waveform overlay.',
    'waveform_opacity': 'Opacity of the waveform overlay.',
    'waveform_scale': 'Vertical scale of the waveform.',
    'waveform_style': 'Center draws around the middle line; Bounce grows from the bottom.',
    'waveform_window': 'Seconds of audio shown in the waveform window.',
    'title_toggle': 'Overlay text on the video.',
    'title_text': 'Text to draw on the video.',
    'title_color': 'Color of the title text.',
    'title_size': 'Font size of the title text.',
    'title_x': 'Horizontal title position. 0 = left, 0.5 = center, 1 = right.',
    'title_y': 'Vertical title position. 0 = top, 1 = bottom.',
    'watermark_toggle': 'Overlay a watermark image on the video.',
    'watermark_file': 'Watermark image file.',
    'watermark_size': 'Watermark size relative to the smaller canvas dimension.',
    'watermark_blending': 'Blend mode used to combine the watermark with the frame.',
    'watermark_x': 'Horizontal watermark position. 0 = left, 0.5 = center, 1 = right.',
    'watermark_y': 'Vertical watermark position. 0 = top, 1 = bottom.',
    'post_effect': 'Full-frame post-processing effect applied after everything else.',
    'post_effect_strength': 'Intensity of the post-processing effect.',
    'beat_pulse': 'Pulse the visuals in time with detected beats.',
    'beat_pulse_strength': 'Intensity of the beat pulse.'
}

def _help(name):
    return OPTION_HELP.get(name, '')

_missing_variable = UserVar(None)

def get_variable(name):
    if name in session_variables:
        return session_variables[name]
    if name in preset_variables:
        return preset_variables[name]
    print(f"Provided variable name {name} is invalid.")
    return _missing_variable

def get_value(name):
    variable = get_variable(name)
    if variable:
        return variable.get()

def set_variable(name, value):
    variable = get_variable(name)
    if variable:
        return variable.set(value)

def check_num(newval):
    return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5
def check_float(newval):
    return re.match('^[+-]?(?:[0-9]*[.])?[0-9]*$', newval) is not None and len(newval) <= 5
def check_hex(newval):
    return re.match(r'^#?[0-9a-fA-F]{0,6}$', newval) is not None

# ------------------------------------------------------------------ scheduling / dialogs
_timers = {}

def schedule(timeout_ms, callback):
    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    handle = id(timer)
    _timers[handle] = timer
    def _fire():
        _timers.pop(handle, None)
        try:
            callback()
        finally:
            timer.deleteLater()
    timer.timeout.connect(_fire)
    timer.start(int(timeout_ms))
    return handle

def cancel_scheduled(handle):
    if not handle:
        return
    timer = _timers.pop(handle, None)
    if timer is not None:
        try:
            timer.stop()
            timer.deleteLater()
        except Exception:
            pass

def show_error(title, message):
    QtWidgets.QMessageBox.critical(root, title, message)

def _file_filter(filetypes):
    groups = []
    for name, pattern in filetypes:
        groups.append(f"{name} ({pattern.replace(';', ' ')})")
    return ';;'.join(groups) if groups else 'All files (*)'

def save_filename(filetypes, initialdir, formatInitial=False):
    parent = root if 'root' in globals() and root is not None else None
    start = os.path.abspath('.' + initialdir)
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(parent, 'Save file', start, _file_filter(filetypes))
    if not filename:
        return ''
    return format_path(filename, initialdir if formatInitial else '')

def open_filename(filetypes, initialdir, formatInitial=False, multiple=False):
    parent = root if 'root' in globals() and root is not None else None
    start = os.path.abspath('.' + initialdir)
    filter_text = _file_filter(filetypes)
    if multiple:
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(parent, 'Open files', start, filter_text)
        return '|'.join(format_path(filename, initialdir if formatInitial else '') for filename in filenames)
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', start, filter_text)
    if not filename:
        return ''
    return format_path(filename, initialdir if formatInitial else '')

def _pick_color(name):
    initial = QtGui.QColor(get_value(name) or '#ffffff')
    color = QtWidgets.QColorDialog.getColor(initial, root, 'Pick color')
    if color.isValid():
        set_variable(name, color.name())

def save_preset():
    presetpath = save_filename([DialogFiletypes.jsonPreset], '/presets')
    if not presetpath:
        return
    with open(presetpath, 'w') as jsonoutput:
        preset_json = {}
        for name in all_variable_names:
            preset_json[name] = get_value(name)
        json.dump(preset_json, jsonoutput)

def load_preset():
    presetpath = open_filename([DialogFiletypes.jsonPreset], '/presets')
    if not presetpath:
        return
    preset = json.load(open(presetpath))
    if not isinstance(preset, dict):
        return
    if 'log_freq' in preset and 'freq_scale' not in preset:
        preset['freq_scale'] = 'Logarithmic' if preset['log_freq'] else 'Linear'
    root.setUpdatesEnabled(False)
    begin_bulk_load()
    try:
        for name, value in preset.items():
            set_variable(name, value)
    finally:
        end_bulk_load()
        root.setUpdatesEnabled(True)
        root.update()
    update_encoder_choices()

def compare_versions(a, b):
    a_parts = [int(p) for p in a.split('.')]
    b_parts = [int(p) for p in b.split('.')]
    for i in range(max(len(a_parts), len(b_parts))):
        a_part = a_parts[i] if i < len(a_parts) else 0
        b_part = b_parts[i] if i < len(b_parts) else 0
        if a_part != b_part:
            return 1 if a_part > b_part else -1
    if len(a_parts) != len(b_parts):
        return 1 if len(a_parts) > len(b_parts) else -1
    return 0

def check_version():
    def fetch():
        try:
            with urllib.request.urlopen("https://raw.githubusercontent.com/TerribleAtCreating/python-mv/main/version.txt", timeout=5) as response:
                latest = response.read().decode('utf-8').strip()
            if compare_versions(currentVersion, latest) < 0:
                schedule(0, lambda: _ask_release(latest))
        except Exception:
            pass
    Thread(target=fetch).start()

def _ask_release(latest):
    answer = QtWidgets.QMessageBox.question(
        root, 'New release available: v' + latest,
        'A new update for this script is available.\nWould you like to be directed to the release page?',
        QtWidgets.QMessageBox.StandardButton.Yes, QtWidgets.QMessageBox.StandardButton.No)
    if answer == QtWidgets.QMessageBox.StandardButton.Yes:
        webbrowser.open("https://github.com/TerribleAtCreating/python-mv/releases/latest", 2, True)

# ------------------------------------------------------------------ encoder choices
encoder_menu = None

def _encoder_choices(fmt):
    fmt_data = OutputFormats.get(fmt)
    choices = []
    if isinstance(fmt_data, dict):
        encoders = fmt_data.get('encoders')
        choices = list(encoders) if encoders else list(fmt_data)
    elif isinstance(fmt_data, (list, tuple)):
        choices = list(fmt_data)
    if not choices and Encoders:
        choices = list(Encoders)
    if not choices:
        choices = [get_value('encoder') or 'Auto']
    return choices

def _choice_codec(choice):
    enc = Encoders.get(choice)
    return enc.get('vcodec') if isinstance(enc, dict) else None

def _encoder_unavailable(fmt):
    unavailable = {}
    for choice in _encoder_choices(fmt):
        codec = _choice_codec(choice)
        if not codec or encoder_available(codec):
            continue
        if 'nvenc' in codec:
            unavailable[choice] = 'Unavailable: your NVIDIA GPU driver does not support this encoder.'
        else:
            unavailable[choice] = 'Unavailable: this encoder is not supported on this system.'
    return unavailable

def update_encoder_choices(*_):
    if encoder_menu is None:
        return
    fmt = get_value('output_format')
    if not fmt:
        return
    encoder_menu.set_choices(_encoder_choices(fmt), _encoder_unavailable(fmt))

# ------------------------------------------------------------------ validation
def _as_num(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None

def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def validate_settings():
    problems = []
    if get_value('batch_mode'):
        if not str(get_value('batch_files') or '').strip():
            problems.append(('batch_files', 'No batch audio files selected.'))
    else:
        try:
            assert_empty(get_value('input_file'), 'Input file')
        except ValueError:
            problems.append(('input_file', 'No input audio file selected.'))

    if not get_value('export_auto'):
        try:
            assert_empty(get_value('export_file'), 'Export file')
        except ValueError:
            problems.append(('export_file', 'No export filename entered (or enable auto naming).'))

    if get_value('bg_style') == 'Image':
        try:
            assert_empty(get_value('background'), 'Background')
        except ValueError:
            problems.append(('background', 'No background image selected.'))

    if get_value('watermark_toggle'):
        try:
            assert_empty(get_value('watermark_file'), 'Watermark')
        except ValueError:
            problems.append(('watermark_file', 'No watermark image selected.'))

    style_checks = [
        ('output_format', OutputFormats, 'Output format'),
        ('video_upscale', ResolutionUpscale, 'Video upscale'),
        ('fft_window', FFTWindows, 'FFT window'),
        ('bar_layout', BarLayouts, 'Bar layout'),
        ('color_style', ColorStyles, 'Color style'),
        ('bg_style', BGStyles, 'Background style'),
        ('watermark_blending', BlendingModes, 'Watermark blending mode')
    ]
    for name, enum, context in style_checks:
        try:
            assert_enum(get_value(name), enum, context)
        except ValueError as error:
            problems.append((name, str(error)))

    start = _as_float(get_value('audio_start'))
    end = _as_float(get_value('audio_end'))
    if start is None:
        start = 0.0
    if end is None:
        end = 0.0
    if end > 0 and end <= start:
        problems.append(('audio_end', 'Audio end time must be after the start time (or 0 for the rest of the file).'))

    framerate = _as_num(get_value('framerate'))
    if framerate is None or framerate < 1:
        problems.append(('framerate', 'Framerate must be at least 1.'))

    bars = _as_num(get_value('bars'))
    if bars is None or bars < 1:
        problems.append(('bars', 'Bar count must be at least 1.'))
    elif bars > 64:
        problems.append(('bars', 'Bar count cannot exceed 64.'))

    quality = _as_num(get_value('quality'))
    if quality is None or not (0 <= quality <= 100):
        problems.append(('quality', 'Quality must be between 0 and 100.'))

    overlap = _as_num(get_value('fft_overlap'))
    if overlap is None or not (0 <= overlap <= 94):
        problems.append(('fft_overlap', 'FFT overlap must be between 0 and 94 percent.'))

    freq_min = _as_num(get_value('freq_min'))
    if freq_min is None or freq_min < 0:
        problems.append(('freq_min', 'Minimum frequency must be 0 or greater.'))
        freq_min = 0

    freq_max = _as_num(get_value('freq_max'))
    if freq_max is None or freq_max <= freq_min:
        problems.append(('freq_max', 'Maximum frequency must be greater than the minimum frequency.'))

    db_range = _as_num(get_value('db_range'))
    if db_range is None or db_range <= 0:
        problems.append(('db_range', 'Dynamic range must be greater than 0.'))

    return (not problems, problems)

def mark_entry(name, valid):
    entry = entry_widgets.get(name)
    if entry is None:
        return
    entry.set_valid(valid)

def highlight_invalid(names):
    for name in entry_widgets:
        mark_entry(name, name not in names)

def set_ui_state(state='normal'):
    for widget in widget_list['render']:
        try:
            widget.configure(state=state)
        except Exception:
            pass

def launch_ui():
    root.show()
    schedule(1500, check_version)
    app.exec_()

# ------------------------------------------------------------------ widgets
entry_widgets = {}
row_widgets = {}
section_widgets = {}
widget_list = {'render': []}

def _repolish(widget):
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()

class QBtn(QtWidgets.QPushButton):
    def __init__(self, text='', accent=False):
        super().__init__(text)
        if accent:
            self.setObjectName('Accent')
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._command = None
        self._cmd_connected = False
    def configure(self, **kw):
        if 'text' in kw:
            self.setText(str(kw['text']))
        if 'command' in kw:
            command = kw.get('command')
            if command is self._command:
                pass
            else:
                if self._cmd_connected:
                    try:
                        self.clicked.disconnect(self._command)
                    except Exception:
                        pass
                    self._cmd_connected = False
                self._command = command
                if self._command is not None:
                    self.clicked.connect(self._command)
                    self._cmd_connected = True
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')

class QLbl(QtWidgets.QLabel):
    def configure(self, **kw):
        if 'text' in kw:
            self.setText(str(kw['text']))
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')

class QChk(QtWidgets.QCheckBox):
    def __init__(self, name, ontext='Enabled', offtext='Disabled'):
        super().__init__()
        self._name = name
        self._on, self._off = ontext, offtext
        self._hover = False
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.toggled.connect(self._on_toggled)
        get_variable(name).trace_add('write', lambda *_: self._update_from_var())
        self._update_from_var()
    def configure(self, **kw):
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)
    def _update_from_var(self):
        self.setText(self._on if bool(get_value(self._name)) else self._off)
    def _on_toggled(self, checked):
        set_variable(self._name, bool(checked))
        self.setText(self._on if checked else self._off)
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        size, x = 16, 2
        y = (rect.height() - size) // 2
        box = QtCore.QRect(x, y, size, size)
        checked = self.isChecked()
        enabled = self.isEnabled()
        fill = QtGui.QColor(ACCENT if checked else FIELD)
        if not enabled:
            fill = QtGui.QColor('#201b15')
        border = QtGui.QColor(ACCENT if checked else ('#4a4134' if self._hover else BORDER))
        painter.setPen(QtGui.QPen(border, 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(box, 4, 4)
        if checked and enabled:
            painter.setPen(QtGui.QPen(QtGui.QColor('#191206'), 2, QtCore.Qt.PenStyle.SolidLine,
                                      QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(QtCore.QPointF(x + 4, y + size * 0.52), QtCore.QPointF(x + size * 0.42, y + size * 0.70))
            painter.drawLine(QtCore.QPointF(x + size * 0.42, y + size * 0.70), QtCore.QPointF(x + size - 3, y + size * 0.22))
        text_rect = QtCore.QRect(x + size + 9, 0, max(rect.width() - x - size - 9, 0), rect.height())
        painter.setPen(QtGui.QPen(QtGui.QColor(FG if enabled else DISABLED_FG), 1))
        painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft, self.text())
        painter.end()

def _var_kind(name):
    value = default_values.get(name)
    if isinstance(value, bool):
        return 'bool'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, int):
        return 'int'
    if isinstance(value, str) and value.startswith('#'):
        return 'hex'
    return 'str'

class QEnt(QtWidgets.QLineEdit):
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._syncing = False
        self._kind = _var_kind(name)
        patterns = {
            'int': r'^[+-]?\d*$',
            'float': r'^[+-]?\d*\.?\d*$',
            'hex': r'^#?[0-9a-fA-F]{0,6}$'
        }
        pattern = patterns.get(self._kind)
        if pattern:
            self.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(pattern), self))
        self.textChanged.connect(self._on_edit)
        get_variable(name).trace_add('write', lambda *_: self._update_from_var())
        self._update_from_var()
    def configure(self, **kw):
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')
    def set_valid(self, valid):
        self.setProperty('invalid', not valid)
        _repolish(self)
    def _on_edit(self, text):
        if self._syncing:
            return
        set_variable(self._name, text)
    def _update_from_var(self):
        if self.hasFocus():
            return
        value = get_value(self._name)
        text = '' if value is None else str(value)
        if text != self.text():
            self._syncing = True
            try:
                self.setText(text)
            finally:
                self._syncing = False

class ArrowCombo(QtWidgets.QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        enabled = self.isEnabled()
        color = QtGui.QColor(MUTED if enabled else DISABLED_FG)
        painter.setPen(QtGui.QPen(color, 1.7, QtCore.Qt.PenStyle.SolidLine,
                                  QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin))
        x, y = self.width() - 16, self.height() // 2
        painter.drawLine(x - 4, y - 2, x, y + 3)
        painter.drawLine(x, y + 3, x + 4, y - 2)
        painter.end()
    def configure(self, **kw):
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')

class QCombo(ArrowCombo):
    def __init__(self, name, values):
        super().__init__()
        self._name = name
        self._syncing = False
        self.setMaxVisibleItems(14)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.currentTextChanged.connect(self._on_current)
        get_variable(name).trace_add('write', lambda *_: self._update_from_var())
        self._syncing = True
        try:
            self.addItems([str(v) for v in values])
            self._update_from_var()
        finally:
            self._syncing = False
    def _update_from_var(self):
        text = str(get_value(self._name))
        index = self.findText(text)
        if index >= 0 and index != self.currentIndex():
            self._syncing = True
            try:
                self.setCurrentIndex(index)
            finally:
                self._syncing = False
    def _on_current(self, text):
        if self._syncing:
            return
        if text != str(get_value(self._name)):
            set_variable(self._name, text)
    def set_choices(self, values, unavailable=None):
        values = [str(v) for v in values]
        unavailable = unavailable or {}
        current = str(get_value(self._name))
        block = self.blockSignals(True)
        self.clear()
        self.addItems(values)
        model = self.model()
        for index, value in enumerate(values):
            item = model.item(index) if isinstance(model, QtGui.QStandardItemModel) else None
            if item is None:
                continue
            tip = unavailable.get(value)
            if tip:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setData(tip, QtCore.Qt.ItemDataRole.ToolTipRole)
        if current in values and current not in unavailable:
            self.setCurrentIndex(values.index(current))
        elif values:
            pick = next((value for value in values if value not in unavailable), values[0])
            self.setCurrentIndex(values.index(pick))
            set_variable(self._name, pick)
        self.blockSignals(block)
        self.update()

class QSld(QtWidgets.QSlider):
    def __init__(self, name):
        super().__init__(QtCore.Qt.Orientation.Horizontal)
        self._name = name
        self._command = None
        self.setRange(0, 100)
        self.setSingleStep(1)
        self.setPageStep(5)
        self.valueChanged.connect(self._on_value)
        get_variable(name).trace_add('write', lambda *_: self._update_from_var())
        self._update_from_var()
    def configure(self, **kw):
        if 'command' in kw:
            self._command = kw.get('command')
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')
    def _on_value(self, value):
        set_variable(self._name, int(value))
        if self._command:
            try:
                self._command(value)
            except Exception:
                traceback.print_exc()
    def _update_from_var(self):
        try:
            value = int(get_value(self._name))
        except (TypeError, ValueError):
            value = 0
        if value != self.value():
            self.setValue(max(0, min(100, value)))

class QProg(QtWidgets.QProgressBar):
    def __init__(self):
        super().__init__()
        self.setRange(0, 1)
        self.setValue(0)
        self.setTextVisible(True)
    def configure(self, **kw):
        if 'maximum' in kw:
            self.setRange(0, max(1, int(kw['maximum'])))
        if 'value' in kw:
            self.setValue(int(kw['value']))
        if 'state' in kw:
            self.setEnabled(kw['state'] == 'normal')
        if 'status' in kw:
            self.setFormat(str(kw['status']))

class CanvasLabel(QLbl):
    def __init__(self):
        super().__init__('No preview yet')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setObjectName('PreviewCanvas')
        self.setMinimumHeight(280)
        self._pixmap = None
        self._drag_origin = None
        self._drag_start = (50.0, 50.0)
    def configure(self, **kw):
        if 'image' in kw:
            self._pixmap = kw['image']
            self._render()
        super().configure(**kw)
    def _render(self):
        if self._pixmap is None or self._pixmap.isNull():
            self.setText('No preview yet')
            self.setPixmap(QtGui.QPixmap())
        else:
            self.setText('')
            self.setPixmap(self._pixmap.scaled(self.size(),
                                               QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                               QtCore.Qt.TransformationMode.SmoothTransformation))
    def _display_size(self):
        pixmap = self._pixmap
        if pixmap is None or pixmap.isNull():
            return None
        pw, ph = pixmap.width(), pixmap.height()
        if pw <= 0 or ph <= 0:
            return None
        scale = min(self.width() / pw, self.height() / ph)
        return (pw * scale, ph * scale)
    def _draggable(self):
        return get_value('bar_position_mode') == 'Exact' and get_value('bar_layout') != 'Radial'
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._draggable():
            self._drag_origin = event.position()
            self._drag_start = (float(get_value('bar_position_x')), float(get_value('bar_position_y')))
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._drag_origin is not None:
            size = self._display_size()
            if size is not None:
                dx = (event.position().x() - self._drag_origin.x()) / max(size[0], 1.0)
                dy = (event.position().y() - self._drag_origin.y()) / max(size[1], 1.0)
                set_variable('bar_position_x', round(max(0.0, min(1.0, self._drag_start[0] / 100.0 + dx)) * 100.0, 1))
                set_variable('bar_position_y', round(max(0.0, min(1.0, self._drag_start[1] / 100.0 + dy)) * 100.0, 1))
                if preview_refresh_hook[0] is not None:
                    preview_refresh_hook[0]()
            event.accept()
            return
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if self._drag_origin is not None:
            self._drag_origin = None
            self.unsetCursor()
        super().mouseReleaseEvent(event)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render()

preview_refresh_hook = [None]

def set_preview_refresh(callback):
    preview_refresh_hook[0] = callback

class Composite(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._items = []
    def add(self, widget):
        self._items.append(widget)
    def configure(self, **kw):
        if 'state' in kw:
            enabled = kw['state'] == 'normal'
            for widget in self._items:
                widget.setEnabled(enabled)

class _EntryHandle:
    def __init__(self, widget):
        self._w = widget
    def set_valid(self, valid):
        self._w.setProperty('invalid', not valid)
        _repolish(self._w)

class SwatchButton(QtWidgets.QPushButton):
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._hover = False
        self.setFixedSize(36, 26)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setToolTip('Open color picker...')
        self.clicked.connect(lambda: _pick_color(name))
        get_variable(name).trace_add('write', lambda *_: self.update())
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        color = QtGui.QColor(get_value(self._name) or '#ffffff')
        border = QtGui.QColor(ACCENT if self._hover else BORDER)
        painter.setPen(QtGui.QPen(border, 1))
        painter.setBrush(color)
        painter.drawRoundedRect(rect, 4, 4)
        painter.end()

def _lerp_hex(hex_a, hex_b, t):
    def parse(value):
        color = QtGui.QColor(str(value))
        if not color.isValid():
            color = QtGui.QColor('#ffffff')
        return color.red(), color.green(), color.blue()
    r1, g1, b1 = parse(hex_a)
    r2, g2, b2 = parse(hex_b)
    t = max(0.0, min(1.0, float(t)))
    return '#%02x%02x%02x' % (round(r1 + (r2 - r1) * t),
                              round(g1 + (g2 - g1) * t),
                              round(b1 + (b2 - b1) * t))

class GradientPicker(QtWidgets.QWidget):
    PAD = 24
    HIT = 12

    def __init__(self, stops_name, fallback_a, fallback_b):
        super().__init__()
        self._stops_name = stops_name
        self._fallback_a = fallback_a
        self._fallback_b = fallback_b
        self._stops = []
        self._guard = False
        self._drag = None
        self._hover = None
        self._selected = None
        self._moved = False
        self.setObjectName('GradientPicker')
        self.setMinimumHeight(36)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        get_variable(fallback_a).trace_add('write', self._fallback_changed)
        get_variable(fallback_b).trace_add('write', self._fallback_changed)
        get_variable(stops_name).trace_add('write', self._stops_changed)
        self._load()
        self.setToolTip('Drag stops to move them.\nDouble-click a stop to change its color.\n'
                        'Double-click the bar to add a stop.\nRight-click a stop to remove it.')

    # -------------------------------------------------- data model
    def _load(self):
        stops = None
        raw = get_value(self._stops_name)
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, list) and len(data) >= 2:
                    parsed = []
                    for item in data:
                        pos = max(0.0, min(1.0, float(item[0])))
                        color = QtGui.QColor(str(item[1]))
                        if not color.isValid():
                            raise ValueError(item[1])
                        parsed.append([pos, color.name().lower()])
                    parsed.sort(key=lambda stop: stop[0])
                    parsed[0][0] = 0.0
                    parsed[-1][0] = 1.0
                    stops = parsed
            except (TypeError, ValueError, IndexError, KeyError):
                stops = None
        if stops is None:
            color_a = QtGui.QColor(str(get_value(self._fallback_a) or '#ffffff'))
            color_b = QtGui.QColor(str(get_value(self._fallback_b) or '#00ccff'))
            if not color_a.isValid():
                color_a = QtGui.QColor('#ffffff')
            if not color_b.isValid():
                color_b = QtGui.QColor('#00ccff')
            stops = [[0.0, color_a.name().lower()], [1.0, color_b.name().lower()]]
        self._stops = stops
        self._save()

    def _save(self):
        self._guard = True
        try:
            set_variable(self._stops_name, json.dumps(self._stops))
            set_variable(self._fallback_a, self._stops[0][1])
            set_variable(self._fallback_b, self._stops[-1][1])
        finally:
            self._guard = False
        self.update()

    def _fallback_changed(self, *_):
        if self._guard or not self._stops:
            return
        first = get_value(self._fallback_a) or '#ffffff'
        last = get_value(self._fallback_b) or '#00ccff'
        if self._stops[0][1] != first or self._stops[-1][1] != last:
            self._stops[0][1] = str(first)
            self._stops[-1][1] = str(last)
            self._save()
        else:
            self.update()

    def _stops_changed(self, *_):
        if self._guard:
            return
        self._load()

    def _color_at(self, pos):
        if pos <= self._stops[0][0]:
            return self._stops[0][1]
        if pos >= self._stops[-1][0]:
            return self._stops[-1][1]
        for i in range(len(self._stops) - 1):
            a, b = self._stops[i], self._stops[i + 1]
            if a[0] <= pos <= b[0]:
                span = b[0] - a[0]
                t = 0.0 if span <= 0 else (pos - a[0]) / span
                return _lerp_hex(a[1], b[1], t)
        return self._stops[-1][1]

    def _insert_stop(self, pos):
        pos = max(0.0, min(1.0, float(pos)))
        stop = [pos, self._color_at(pos)]
        self._stops.append(stop)
        self._stops.sort(key=lambda item: item[0])
        self._save()
        return self._stops.index(stop)

    def _remove_stop(self, index):
        if not isinstance(index, int) or index <= 0 or index >= len(self._stops) - 1:
            return False
        del self._stops[index]
        self._save()
        return True

    def _set_stop_color(self, index, hexcolor):
        if not isinstance(index, int) or not 0 <= index < len(self._stops):
            return False
        color = QtGui.QColor(str(hexcolor))
        if not color.isValid():
            return False
        self._stops[index][1] = color.name().lower()
        self._save()
        return True

    # -------------------------------------------------- geometry
    def _track(self):
        w = self.width()
        return self.PAD, max(w - self.PAD, self.PAD + 1)

    def _stop_x(self, pos):
        x0, x1 = self._track()
        return x0 + pos * (x1 - x0)

    def _pos_from_x(self, x):
        x0, x1 = self._track()
        return max(0.0, min(1.0, (x - x0) / max(x1 - x0, 1.0)))

    def _hit_stop(self, x):
        best = None
        best_dist = None
        for index, stop in enumerate(self._stops):
            dist = abs(x - self._stop_x(stop[0]))
            if best_dist is None or dist < best_dist:
                best, best_dist = index, dist
        if best is not None and best_dist <= self.HIT:
            return best
        return None

    # -------------------------------------------------- events
    def _pick_color(self, index):
        if not 0 <= index < len(self._stops):
            return
        try:
            initial = QtGui.QColor(self._stops[index][1])
            color = QtWidgets.QColorDialog.getColor(initial, root, 'Pick gradient stop color')
        except Exception:
            return
        if color.isValid():
            self._set_stop_color(index, color.name())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            index = self._hit_stop(event.position().x())
            if index is not None:
                self._remove_stop(index)
            event.accept()
            return
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        self._drag = self._hit_stop(event.position().x())
        self._selected = self._drag
        self._moved = False
        self.update()
        event.accept()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._drag is None:
            self._hover = self._hit_stop(event.position().x())
            self.update()
            return
        if 0 < self._drag < len(self._stops) - 1:
            stop = self._stops.pop(self._drag)
            stop[0] = self._pos_from_x(event.position().x())
            insert_at = 0
            for i, other in enumerate(self._stops):
                if other[0] <= stop[0]:
                    insert_at = i + 1
            self._stops.insert(insert_at, stop)
            self._drag = insert_at
            self._selected = insert_at
            self._moved = True
            self._save()
        self.update()

    def mouseReleaseEvent(self, event):
        self._drag = None
        self.update()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            super().mouseDoubleClickEvent(event)
            return
        index = self._hit_stop(event.position().x())
        if index is not None:
            self._pick_color(index)
        else:
            self._insert_stop(self._pos_from_x(event.position().x()))
        event.accept()

    def leaveEvent(self, event):
        self._hover = None
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        x0, x1 = self._track()
        grad_top = 7
        grad_bottom = max(h - 14, grad_top + 4)
        grad_rect = QtCore.QRect(int(x0), grad_top, max(int(x1 - x0), 2), grad_bottom - grad_top)
        linear = QtGui.QLinearGradient(x0, 0, x1, 0)
        for pos, color in self._stops:
            linear.setColorAt(pos, QtGui.QColor(color))
        painter.setPen(QtGui.QPen(QtGui.QColor('#000000'), 1))
        painter.setBrush(linear)
        painter.drawRect(grad_rect)
        for index, (pos, color) in enumerate(self._stops):
            sx = int(self._stop_x(pos))
            stop = QtCore.QRect(sx - 8, grad_top - 2, 16, grad_bottom - grad_top + 4)
            active = self._drag == index or self._hover == index or self._selected == index
            outline = QtGui.QColor(ACCENT if active else '#6b5f48')
            painter.setPen(QtGui.QPen(QtGui.QColor('#100d09'), 1))
            painter.setBrush(QtGui.QColor(color))
            painter.drawRoundedRect(stop, 3, 3)
            painter.setPen(QtGui.QPen(outline, 1.5))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(stop, 3, 3)
        painter.end()

# ------------------------------------------------------------------ layout builders
def _section(container, text, key=None):
    header = QtWidgets.QLabel(text)
    header.setObjectName('Section')
    container.addWidget(header)
    line = QtWidgets.QFrame()
    line.setObjectName('HLine')
    line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
    container.addWidget(line)
    if key is not None:
        section_widgets[key] = (header, line)

def _row(container, text, control, name=None):
    row = QtWidgets.QWidget()
    row.setObjectName('Row')
    layout = QtWidgets.QHBoxLayout(row)
    layout.setContentsMargins(0, 4, 0, 4)
    layout.setSpacing(14)
    label = QtWidgets.QLabel(text)
    label.setObjectName('FieldLabel')
    label.setMinimumWidth(205)
    label.setMaximumWidth(280)
    layout.addWidget(label)
    layout.addWidget(control, 1)
    container.addWidget(row)
    if name is not None:
        row_widgets[name] = row
    help_text = _help(name)
    if help_text:
        tooltip = f'<b>{text}</b><br>{help_text}'
        control.setToolTip(tooltip)
        label.setToolTip(tooltip)
    widget_list['render'].append(control)

def _entry(container, text, name):
    ent = QEnt(name)
    entry_widgets[name] = _EntryHandle(ent)
    _row(container, text, ent, name)

def _checkbox(container, text, name, ontext, offtext):
    _row(container, text, QChk(name, ontext, offtext), name)

def _optionmenu(container, text, name, values):
    _row(container, text, QCombo(name, values), name)

def _color_row(container, text, name):
    ent = QEnt(name)
    swatch = SwatchButton(name)
    group = Composite()
    group.add(ent)
    group.add(swatch)
    layout = QtWidgets.QHBoxLayout(group)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(ent, 1)
    layout.addWidget(swatch)
    entry_widgets[name] = ent
    _row(container, text, group, name)

def _gradient_row(container, label, stops_name, fallback_a, fallback_b):
    picker = GradientPicker(stops_name, fallback_a, fallback_b)
    _row(container, label, picker, stops_name)

def _file_row(container, text, name, filetypes, multiple=False, save=False, initialdir='/files'):
    ent = QtWidgets.QLineEdit()
    ent.setReadOnly(True)
    ent.setPlaceholderText('No file selected')
    ent.setObjectName('FileEnt')
    btn = QBtn('Browse...')
    group = Composite()
    group.add(ent)
    group.add(btn)
    layout = QtWidgets.QHBoxLayout(group)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(ent, 1)
    layout.addWidget(btn)
    def browse():
        chosen = save_filename(filetypes, initialdir, True) if save else open_filename(
            filetypes, initialdir, True, multiple=multiple)
        if chosen:
            set_variable(name, chosen)
    btn.clicked.connect(browse)
    get_variable(name).trace_add('write', lambda *_: ent.setText(str(get_value(name)) if get_value(name) else ''))
    entry_widgets[name] = _EntryHandle(ent)
    _row(container, text, group, name)

def _set_row_visible(name, visible):
    row = row_widgets.get(name)
    if row is not None:
        row.setVisible(visible)

def _set_section_visible(key, visible):
    widgets = section_widgets.get(key)
    if widgets:
        for widget in widgets:
            widget.setVisible(visible)

def _as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

_bulk_load = {'active': False, 'dirty': False}

def begin_bulk_load():
    _bulk_load['active'] = True

def end_bulk_load():
    _bulk_load['active'] = False
    if _bulk_load['dirty']:
        _bulk_load['dirty'] = False
        _apply_visibility()

def _apply_visibility(*_):
    if _bulk_load['active']:
        _bulk_load['dirty'] = True
        return
    batch = bool(get_value('batch_mode'))
    _set_row_visible('input_file', not batch)
    _set_row_visible('batch_files', batch)
    _set_row_visible('export_file', not bool(get_value('export_auto')))

    output_format = get_value('output_format')
    has_encoder = output_format not in ('PNG sequence', 'GIF')
    _set_row_visible('encoder', has_encoder)
    _set_row_visible('quality', has_encoder)
    _set_row_visible('max_output_size', has_encoder)
    _set_row_visible('audio_copy', output_format == 'MP4')
    _set_row_visible('bg_transparent', output_format == 'PNG sequence')

    bg_style = get_value('bg_style')
    _set_row_visible('background', bg_style in ('Image', 'Video'))
    _set_row_visible('video_upscale', bg_style in ('Image', 'Video'))
    _set_row_visible('bg_darken', bg_style in ('Image', 'Video'))
    _set_row_visible('bg_blur', bg_style in ('Image', 'Video'))
    _set_row_visible('bg_solid_color', bg_style == 'Solid')
    _set_row_visible('bg_stops', bg_style == 'Gradient')

    zoom = bool(get_value('bg_zoom'))
    _set_row_visible('bg_zoom_amount', zoom)
    _set_row_visible('bg_zoom_cycles', zoom)
    pan = bool(get_value('bg_pan'))
    _set_row_visible('bg_pan_x', pan)
    _set_row_visible('bg_pan_y', pan)
    _set_row_visible('bg_pan_speed', pan)
    blur = bool(get_value('bg_blur_pulse'))
    _set_row_visible('bg_blur_amount', blur)
    _set_row_visible('bg_blur_response', blur)

    waveform = bool(get_value('waveform_toggle'))
    for name in ('waveform_color', 'waveform_opacity', 'waveform_scale', 'waveform_style', 'waveform_window'):
        _set_row_visible(name, waveform)

    title = bool(get_value('title_toggle'))
    for name in ('title_text', 'title_color', 'title_size', 'title_x', 'title_y'):
        _set_row_visible(name, title)

    watermark = bool(get_value('watermark_toggle'))
    for name in ('watermark_file', 'watermark_size', 'watermark_blending', 'watermark_x', 'watermark_y'):
        _set_row_visible(name, watermark)

    smoothing = bool(get_value('smoothing_enabled'))
    _set_row_visible('attack_alpha', smoothing)
    _set_row_visible('decay_fast', smoothing)

    radial = get_value('bar_layout') == 'Radial'
    _set_section_visible('radial', radial)
    for name in ('radial_radius', 'radial_thickness', 'radial_start', 'radial_sweep', 'radial_margin', 'radial_rotation'):
        _set_row_visible(name, radial)
    for name in ('mirror', 'bar_spacing', 'coverage_x', 'bar_justify_x', 'bar_justify_y', 'bar_reflection', 'bar_peak_caps'):
        _set_row_visible(name, not radial)
    _set_row_visible('bar_peak_size', bool(get_value('bar_peak_caps')) and not radial)
    _set_section_visible('bar_position', not radial)
    exact = get_value('bar_position_mode') == 'Exact' and not radial
    _set_row_visible('bar_position_mode', not radial)
    _set_row_visible('bar_position_x', exact)
    _set_row_visible('bar_position_y', exact)
    _set_row_visible('reflection_strength', bool(get_value('bar_reflection')) and not radial)
    _set_row_visible('outline_color', _as_number(get_value('outline_width')) > 0)

    color_style = get_value('color_style')
    _set_row_visible('color_stops', color_style in ('Brightness', 'Gradient'))
    _set_row_visible('color_a', color_style == 'Solid')
    _set_section_visible('rainbow', color_style == 'Rainbow')
    for name in ('rainbow_saturation', 'rainbow_hue', 'rainbow_cycles'):
        _set_row_visible(name, color_style == 'Rainbow')

    glow = bool(get_value('effect_glow'))
    _set_row_visible('glow_radius', glow)
    _set_row_visible('glow_strength', glow)
    trails = bool(get_value('effect_trails'))
    _set_row_visible('trail_alpha', trails)
    _set_row_visible('trail_scale', trails)

    _set_row_visible('post_effect_strength', get_value('post_effect') != 'None')
    _set_row_visible('beat_pulse_strength', bool(get_value('beat_pulse')))
    taper = _as_number(get_value('edge_taper'))
    for name in ('edge_taper_left', 'edge_taper_right', 'edge_taper_curve'):
        _set_row_visible(name, taper > 0.0)
    vocal = _as_number(get_value('vocal_boost'))
    for name in ('vocal_center', 'vocal_width'):
        _set_row_visible(name, vocal != 0.0)

def _bind_visibility():
    sources = ('batch_mode', 'export_auto', 'output_format', 'bg_style', 'bg_zoom', 'bg_pan',
               'bg_blur_pulse', 'waveform_toggle', 'title_toggle', 'watermark_toggle',
               'smoothing_enabled', 'bar_layout', 'outline_width', 'bar_reflection', 'color_style',
               'effect_glow', 'effect_trails', 'bar_position_mode',
               'post_effect', 'beat_pulse', 'bar_peak_caps', 'edge_taper', 'vocal_boost')
    for name in sources:
        get_variable(name).trace_add('write', _apply_visibility)
    _apply_visibility()

def _make_tab():
    content = QtWidgets.QWidget()
    content.setObjectName('TabContent')
    layout = QtWidgets.QVBoxLayout(content)
    layout.setContentsMargins(18, 12, 18, 18)
    layout.setSpacing(2)
    layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    return scroll, content, layout

# ------------------------------------------------------------------ build window
shared_ui = {}  # holds the tab bar, notebook and control widgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 660)
        self._root_panel = None
    def set_root_panel(self, panel):
        self._root_panel = panel
    def withdraw(self):
        self.hide()

def _build_main_window():
    window = MainWindow()
    window.setObjectName('MainWindow')
    window.setWindowTitle('Python-MV [' + currentVersion + versionStatus + ']')
    gutter = QtWidgets.QWidget(window)
    gutter_layout = QtWidgets.QVBoxLayout(gutter)
    gutter_layout.setContentsMargins(0, 0, 0, 0)
    gutter_layout.setSpacing(0)
    window.setCentralWidget(gutter)

    panel = QtWidgets.QFrame()
    panel.setObjectName('RootPanel')
    panel_layout = QtWidgets.QVBoxLayout(panel)
    panel_layout.setContentsMargins(0, 0, 0, 0)
    panel_layout.setSpacing(0)
    window.set_root_panel(panel)

    tabs = QtWidgets.QTabWidget()
    tabs.setObjectName('Tabs')
    tabs.setDocumentMode(False)
    panel_layout.addWidget(tabs, 1)

    # ---- Main tab ----
    m_scroll, m_content, m_layout = _make_tab()
    _section(m_layout, 'Import & export')
    _file_row(m_layout, 'Input audio', 'input_file', [DialogFiletypes.audio], initialdir='/files')
    _checkbox(m_layout, 'Input mode', 'batch_mode', 'Batch', 'Single')
    _file_row(m_layout, 'Batch audio files', 'batch_files', [DialogFiletypes.audio], multiple=True, initialdir='/files')
    _file_row(m_layout, 'Export filename', 'export_file', [DialogFiletypes.mp4], save=True, initialdir='/export')
    _checkbox(m_layout, 'Export name', 'export_auto', 'Auto name', 'Manual name')
    _section(m_layout, 'Encoding & output')
    _optionmenu(m_layout, 'Output format', 'output_format', list(OutputFormats.keys()))
    global encoder_menu
    encoder_menu = QCombo('encoder', _encoder_choices(get_value('output_format')))
    _row(m_layout, 'Encoder', encoder_menu, 'encoder')
    _entry(m_layout, 'Quality (0-100)', 'quality')
    _optionmenu(m_layout, 'Encoding speed', 'encoder_speed', list(EncoderSpeeds.keys()))
    _entry(m_layout, 'Max output size (MB, 0 = Unlimited)', 'max_output_size')
    _checkbox(m_layout, 'Copy audio track', 'audio_copy', 'Enabled', 'Disabled')
    _optionmenu(m_layout, 'Video upscale', 'video_upscale', list(ResolutionUpscale.keys()))
    _entry(m_layout, 'Framerate', 'framerate')
    _entry(m_layout, 'Resolution width (0 = Automatic)', 'resolution_width')
    _entry(m_layout, 'Resolution height (0 = Automatic)', 'resolution_height')
    _entry(m_layout, 'Start (s)', 'audio_start')
    _entry(m_layout, 'End (s)', 'audio_end')
    tabs.addTab(m_scroll, 'Main')

    # ---- Audio tab ----
    a_scroll, a_content, a_layout = _make_tab()
    _section(a_layout, 'Input analysis')
    _entry(a_layout, 'Channel panning', 'channel_pan')
    _entry(a_layout, 'Gain (dB)', 'gain_db')
    _checkbox(a_layout, 'Normalize audio', 'normalize', 'Enabled', 'Disabled')
    _entry(a_layout, 'Bass boost (0-3)', 'bass_boost')
    _entry(a_layout, 'Bass crossover (Hz)', 'bass_crossover')
    _section(a_layout, 'Spectrum')
    _optionmenu(a_layout, 'FFT size', 'fft_size', ['256', '512', '1024', '2048', '4096', '8192', '16384'])
    _entry(a_layout, 'FFT overlap (0-94%)', 'fft_overlap')
    _optionmenu(a_layout, 'Window function', 'fft_window', list(FFTWindows.keys()))
    _optionmenu(a_layout, 'Frequency scale', 'freq_scale', list(FreqScales.keys()))
    _entry(a_layout, 'Minimum frequency (Hz)', 'freq_min')
    _entry(a_layout, 'Maximum frequency (Hz)', 'freq_max')
    _entry(a_layout, 'Noise floor (dB)', 'noise_floor')
    _entry(a_layout, 'Dynamic range (dB)', 'db_range')
    _optionmenu(a_layout, 'Band measure', 'band_measure', list(BandMeasures.keys()))
    _entry(a_layout, 'Spectral tilt (dB/oct)', 'spectral_tilt')
    _entry(a_layout, 'Vocal boost (dB)', 'vocal_boost')
    _entry(a_layout, 'Vocal center (Hz)', 'vocal_center')
    _entry(a_layout, 'Vocal width (oct)', 'vocal_width')
    _entry(a_layout, 'Edge taper (0-1)', 'edge_taper')
    _entry(a_layout, 'Edge taper left', 'edge_taper_left')
    _entry(a_layout, 'Edge taper right', 'edge_taper_right')
    _optionmenu(a_layout, 'Edge taper curve', 'edge_taper_curve', list(TaperCurves.keys()))
    tabs.addTab(a_scroll, 'Audio')

    # ---- Timing tab ----
    t_scroll, t_content, t_layout = _make_tab()
    _section(t_layout, 'Bar smoothing')
    _checkbox(t_layout, 'Smoothing', 'smoothing_enabled', 'Enabled', 'Disabled')
    _entry(t_layout, 'Attack alpha', 'attack_alpha')
    _entry(t_layout, 'Decay alpha', 'decay_alpha')
    _entry(t_layout, 'Fast decay multiplier', 'decay_fast')
    _entry(t_layout, 'Lookahead offset (s)', 'timing_offset')
    tabs.addTab(t_scroll, 'Timing')

    # ---- Bars tab ----
    b_scroll, b_content, b_layout = _make_tab()
    _section(b_layout, 'Bar layout')
    _entry(b_layout, 'Number of bars', 'bars')
    _optionmenu(b_layout, 'Bar layout', 'bar_layout', list(BarLayouts.keys()))
    _entry(b_layout, 'Bar spacing (px)', 'bar_spacing')
    _checkbox(b_layout, 'Mirror', 'mirror', 'Mirrored', 'Not mirrored')
    _section(b_layout, 'Sizing & shaping')
    _entry(b_layout, 'Coverage width', 'coverage_x')
    _entry(b_layout, 'Coverage height', 'coverage_y')
    _entry(b_layout, 'Justify X', 'bar_justify_x')
    _entry(b_layout, 'Justify Y', 'bar_justify_y')
    _entry(b_layout, 'Bar length scale', 'bar_scale')
    _entry(b_layout, 'Height exponent', 'height_exp')
    _entry(b_layout, 'Brightness exponent', 'brightness_exp')
    _entry(b_layout, 'Corner radius (px)', 'corner_radius')
    _entry(b_layout, 'Outline width (px)', 'outline_width')
    _color_row(b_layout, 'Outline color', 'outline_color')
    _checkbox(b_layout, 'Reflection', 'bar_reflection', 'Enabled', 'Disabled')
    _entry(b_layout, 'Reflection strength', 'reflection_strength')
    _checkbox(b_layout, 'Peak caps', 'bar_peak_caps', 'Enabled', 'Disabled')
    _entry(b_layout, 'Peak cap height (px)', 'bar_peak_size')
    _section(b_layout, 'Bar position', 'bar_position')
    _optionmenu(b_layout, 'Position mode', 'bar_position_mode', list(BarPositionModes.keys()))
    _entry(b_layout, 'Position X (%)', 'bar_position_x')
    _entry(b_layout, 'Position Y (%)', 'bar_position_y')
    _section(b_layout, 'Radial mode', 'radial')
    _entry(b_layout, 'Base radius', 'radial_radius')
    _entry(b_layout, 'Thickness', 'radial_thickness')
    _entry(b_layout, 'Start angle (deg)', 'radial_start')
    _entry(b_layout, 'Sweep (deg)', 'radial_sweep')
    _entry(b_layout, 'Bar margin (deg)', 'radial_margin')
    _entry(b_layout, 'Rotation cycles', 'radial_rotation')
    tabs.addTab(b_scroll, 'Bars')

    # ---- Colors tab ----
    c_scroll, c_content, c_layout = _make_tab()
    _section(c_layout, 'Bar coloring')
    _optionmenu(c_layout, 'Color style', 'color_style', list(ColorStyles.keys()))
    _gradient_row(c_layout, 'Gradient colors', 'color_stops', 'color_a', 'color_b')
    _color_row(c_layout, 'Bar color', 'color_a')
    _section(c_layout, 'Rainbow', 'rainbow')
    _entry(c_layout, 'Saturation', 'rainbow_saturation')
    _entry(c_layout, 'Hue offset (deg)', 'rainbow_hue')
    _entry(c_layout, 'Cycles', 'rainbow_cycles')
    _section(c_layout, 'Glow & trails')
    _checkbox(c_layout, 'Glow effect', 'effect_glow', 'Enabled', 'Disabled')
    _entry(c_layout, 'Glow radius (px)', 'glow_radius')
    _entry(c_layout, 'Glow strength', 'glow_strength')
    _checkbox(c_layout, 'Trails', 'effect_trails', 'Enabled', 'Disabled')
    _entry(c_layout, 'Trail fade', 'trail_alpha')
    _entry(c_layout, 'Trail scale', 'trail_scale')
    _section(c_layout, 'Background colors')
    _optionmenu(c_layout, 'Background style', 'bg_style', list(BGStyles.keys()))
    _color_row(c_layout, 'Solid color', 'bg_solid_color')
    _checkbox(c_layout, 'Transparent background', 'bg_transparent', 'Transparent', 'Opaque')
    _gradient_row(c_layout, 'Background gradient', 'bg_stops', 'bg_grad_a', 'bg_grad_b')
    tabs.addTab(c_scroll, 'Colors')

    # ---- Effects tab ----
    e_scroll, e_content, e_layout = _make_tab()
    _section(e_layout, 'Background')
    _file_row(e_layout, 'Background image / video', 'background', [DialogFiletypes.png, DialogFiletypes.jpg, DialogFiletypes.video], initialdir='/files')
    _entry(e_layout, 'Darken background (0-1)', 'bg_darken')
    _entry(e_layout, 'Background blur (px)', 'bg_blur')
    _section(e_layout, 'Background animation')
    _checkbox(e_layout, 'Zoom', 'bg_zoom', 'Enabled', 'Disabled')
    _entry(e_layout, 'Zoom amount', 'bg_zoom_amount')
    _entry(e_layout, 'Zoom cycles', 'bg_zoom_cycles')
    _checkbox(e_layout, 'Pan', 'bg_pan', 'Enabled', 'Disabled')
    _entry(e_layout, 'Pan X', 'bg_pan_x')
    _entry(e_layout, 'Pan Y', 'bg_pan_y')
    _entry(e_layout, 'Pan speed', 'bg_pan_speed')
    _checkbox(e_layout, 'Blur pulse', 'bg_blur_pulse', 'Enabled', 'Disabled')
    _entry(e_layout, 'Blur amount (px)', 'bg_blur_amount')
    _entry(e_layout, 'Blur response', 'bg_blur_response')
    _section(e_layout, 'Post processing')
    _optionmenu(e_layout, 'Post effect', 'post_effect', POST_EFFECT_NAMES)
    _entry(e_layout, 'Post effect strength', 'post_effect_strength')
    _checkbox(e_layout, 'Beat pulse', 'beat_pulse', 'Enabled', 'Disabled')
    _entry(e_layout, 'Beat pulse strength', 'beat_pulse_strength')
    _section(e_layout, 'Waveform overlay')
    _checkbox(e_layout, 'Show waveform', 'waveform_toggle', 'Enabled', 'Disabled')
    _color_row(e_layout, 'Waveform color', 'waveform_color')
    _entry(e_layout, 'Waveform opacity', 'waveform_opacity')
    _entry(e_layout, 'Waveform scale', 'waveform_scale')
    _optionmenu(e_layout, 'Waveform style', 'waveform_style', ['Center', 'Bounce'])
    _entry(e_layout, 'Waveform window (s)', 'waveform_window')
    _section(e_layout, 'Title overlay')
    _checkbox(e_layout, 'Show title', 'title_toggle', 'Enabled', 'Disabled')
    _entry(e_layout, 'Title text', 'title_text')
    _color_row(e_layout, 'Title color', 'title_color')
    _entry(e_layout, 'Title size', 'title_size')
    _entry(e_layout, 'Title X', 'title_x')
    _entry(e_layout, 'Title Y', 'title_y')
    tabs.addTab(e_scroll, 'Effects')

    # ---- Watermark tab ----
    w_scroll, w_content, w_layout = _make_tab()
    _section(w_layout, 'Watermark')
    _checkbox(w_layout, 'Toggle watermark', 'watermark_toggle', 'Enabled', 'Disabled')
    _file_row(w_layout, 'Watermark image', 'watermark_file', [DialogFiletypes.png, DialogFiletypes.jpg, DialogFiletypes.gif], initialdir='/files')
    _entry(w_layout, 'Watermark size (0-1)', 'watermark_size')
    _optionmenu(w_layout, 'Blending mode', 'watermark_blending', list(BlendingModes.keys()))
    _entry(w_layout, 'Position X', 'watermark_x')
    _entry(w_layout, 'Position Y', 'watermark_y')
    tabs.addTab(w_scroll, 'Watermark')

    # ---- Preview tab ----
    p_scroll, p_content, p_layout = _make_tab()
    _section(p_layout, 'Preview')
    slider = QSld('preview_position')
    _row(p_layout, 'Frame position (%)', slider, 'preview_position')
    refresh_button = QBtn('Refresh frame')
    save_button = QBtn('Save preview PNG')
    button_row = Composite()
    button_row.add(refresh_button)
    button_row.add(save_button)
    row_layout = QtWidgets.QHBoxLayout(button_row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(8)
    for btn in (refresh_button, save_button):
        btn.setFixedHeight(30)
        row_layout.addWidget(btn)
    _row(p_layout, 'Preview actions', button_row)
    canvas = CanvasLabel()
    info = QLbl('Ready')
    info.setObjectName('Status')
    info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    p_layout.addWidget(canvas, 1)
    p_layout.addWidget(info)
    widget_list['render'].extend([slider, refresh_button, save_button, canvas, info])
    tabs.addTab(p_scroll, 'Preview')

    # ---- bottom control bar ----
    bottom = QtWidgets.QWidget()
    bottom.setObjectName('BottomBar')
    bottom_layout = QtWidgets.QVBoxLayout(bottom)
    bottom_layout.setContentsMargins(16, 10, 16, 14)
    bottom_layout.setSpacing(8)
    actions = QtWidgets.QHBoxLayout()
    actions.setSpacing(8)
    save_preset_btn = QBtn('Save Preset')
    load_preset_btn = QBtn('Load Preset')
    save_preset_btn.setObjectName('Ghost')
    load_preset_btn.setObjectName('Ghost')
    save_preset_btn.clicked.connect(save_preset)
    load_preset_btn.clicked.connect(load_preset)
    actions.addWidget(save_preset_btn)
    actions.addWidget(load_preset_btn)
    actions.addStretch(1)
    preview_btn = QBtn('Preview')
    render_btn = QBtn('Render', accent=True)
    actions.addWidget(preview_btn)
    actions.addWidget(render_btn)
    bottom_layout.addLayout(actions)
    progress_bar = QProg()
    progress_bar.setObjectName('Progress')
    progress_label = QLbl('Ready')
    progress_label.setObjectName('Status')
    bottom_layout.addWidget(progress_bar)
    bottom_layout.addWidget(progress_label)

    panel_layout.addWidget(bottom)
    gutter_layout.addWidget(panel)
    window.set_root_panel(panel)

    widget_list['render'].extend([render_btn, preview_btn])

    shared_ui.update({
        'tabs': tabs,
        'continue_button': render_btn,
        'preview_button': preview_btn,
        'progress_bar': progress_bar,
        'progress_label': progress_label,
        'preview_slider': slider,
        'preview_refresh_button': refresh_button,
        'preview_save_button': save_button,
        'preview_canvas': canvas,
        'preview_info_label': info,
        'save_preset_btn': save_preset_btn,
        'load_preset_btn': load_preset_btn
    })
    _bind_visibility()
    return window

get_variable('output_format').trace_add('write', update_encoder_choices)

root = _build_main_window()

continue_button = shared_ui['continue_button']
preview_button = shared_ui['preview_button']
progress_bar = shared_ui['progress_bar']
progress_label = shared_ui['progress_label']
preview_slider = shared_ui['preview_slider']
preview_refresh_button = shared_ui['preview_refresh_button']
preview_save_button = shared_ui['preview_save_button']
preview_canvas = shared_ui['preview_canvas']
preview_info_label = shared_ui['preview_info_label']
update_encoder_choices()

def pil_to_pixmap(image):
    rgb = image.convert('RGB')
    data = rgb.tobytes('raw', 'RGB')
    qimage = QtGui.QImage(data, rgb.size[0], rgb.size[1], rgb.size[0] * 3, QtGui.QImage.Format.Format_RGB888)
    return QtGui.QPixmap.fromImage(qimage)