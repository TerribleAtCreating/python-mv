from import_modules import *
from resources import *

root = tkinter.Tk()
root.title("Python-MV")
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('terriac.pythonmv')
root.iconbitmap("pymv.ico", "pymv.ico")

input_file = tkinter.StringVar()
export_file = tkinter.StringVar()
channel_pan = tkinter.StringVar()

defaultpreset = {
    "channel_pan": .5,
    "framerate": 30,
    "bars": 25,
    "bar_spacing": 5,
    "lerp_alpha": .75,
    "lerp_speed": 25,
    "coverage_x": 1,
    "coverage_y": .5,
    "bar_justify_x": .5,
    "bar_justify_y": 1,
    "brightness_exp": 0,
    "height_exp": .5
}

justify_horizontal = [
"Left",
"Center",
"Right"
]
justify_vertical = [
"Top",
"Center",
"Bottom"
]

channel_pan = tkinter.StringVar(value=defaultpreset.get("channel_pan"))

framerate = tkinter.StringVar(value=defaultpreset.get("framerate"))
bars = tkinter.StringVar(value=defaultpreset.get("bars"))
bar_spacing = tkinter.StringVar(value=defaultpreset.get("bar_spacing"))
lerp_alpha = tkinter.StringVar(value=defaultpreset.get("lerp_alpha"))
lerp_speed = tkinter.StringVar(value=defaultpreset.get("lerp_speed"))
background = tkinter.StringVar(value=defaultpreset.get("background"))

coverage_x = tkinter.StringVar(value=defaultpreset.get("coverage_x"))
coverage_y = tkinter.StringVar(value=defaultpreset.get("coverage_y"))
bar_justify_x = tkinter.StringVar(value=defaultpreset.get("bar_justify_x"))
bar_justify_y = tkinter.StringVar(value=defaultpreset.get("bar_justify_y"))
brightness_exp = tkinter.StringVar(value=defaultpreset.get("brightness_exp"))
height_exp = tkinter.StringVar(value=defaultpreset.get("height_exp"))

check_num_wrapper = (root.register(check_num), '%P')
check_float_wrapper = (root.register(check_float), '%P')

# Dialog buttons
def save_preset():
    presetpath = save_filename([('JSON Preset', '*.json')], '/presets')
    if not presetpath: return
    with open(presetpath, 'w') as jsonoutput:
        json.dump({
            "channelpan": float(channel_pan.get()),
            
            "framerate": int(framerate.get()),
            "bars": int(bars.get()),
            "bar_spacing": int(bar_spacing.get()),
            "lerp_alpha": float(lerp_alpha.get()),
            "lerp_speed": float(lerp_speed.get()),
            "background": background.get(),
            
            "coverage_x": float(coverage_x.get()),
            "coverage_y": float(coverage_y.get()),
            "bar_justify_x": float(bar_justify_x.get()),
            "bar_justify_y": float(bar_justify_y.get()),
            "brightness_exp": float(brightness_exp.get()),
            "height_exp": float(height_exp.get())
            }, jsonoutput)
def load_preset():
    presetpath = open_filename([('JSON Preset', '*.json')], '/presets')
    if not presetpath: return
    if not os.path.isfile(presetpath):
        tkinter.messagebox.showwarning("File not found", "Selected file does not exist.")
        return
    preset: dict = json.load(open(presetpath))
    
    channel_pan.set(preset.get("channel_pan", defaultpreset.get("channel_pan")))
    
    framerate.set(preset.get("framerate", defaultpreset.get("framerate")))
    bars.set(preset.get("bars", defaultpreset.get("bars")))
    bar_spacing.set(preset.get("bar_spacing", defaultpreset.get("bar_spacing")))
    lerp_alpha.set(preset.get("lerp_alpha", defaultpreset.get("lerp_alpha")))
    lerp_speed.set(preset.get("lerp_speed", defaultpreset.get("lerp_speed")))
    background.set(preset.get("background", defaultpreset.get("background")))
    
    coverage_x.set(preset.get("coverage_x", defaultpreset.get("coverage_x")))
    coverage_y.set(preset.get("coverage_y", defaultpreset.get("coverage_y")))
    bar_justify_x.set(preset.get("bar_justify_x", defaultpreset.get("bar_justify_x")))
    bar_justify_y.set(preset.get("bar_justify_y", defaultpreset.get("bar_justify_y")))
    brightness_exp.set(preset.get("brightness_exp", defaultpreset.get("brightness_exp")))
    height_exp.set(preset.get("height_exp", defaultpreset.get("height_exp")))

widget_list = dict()
# Layout: [(Element, X, Y, Widthspan, Heightspan)]
layout = {
    "import/export": [
        (tkinter.Label(root, text="Import/Export:"), 0, 0, 2, 1),
        (tkinter.Label(root, text="Input file (.wav):"), 0, 1, 1, 1), (OpenFileMenu(root, text="Select audio...", targetvariable=input_file, filetypes=[('Wave audio file', '*.wav')], initialdir='/files'), 1, 1, 1, 1),
        (tkinter.Label(root, text="Export filename:"), 0, 2, 1, 1), (SaveFileMenu(root, text="Select filename...", targetvariable=export_file, filetypes=[('MPEG-4 video file', '*.mp4')], initialdir='/export'), 1, 2, 1, 1),
        (tkinter.Label(root, text="Channel panning:"), 0, 3, 1, 1), (tkinter.Entry(root, textvariable=channel_pan, validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
    ],
    "render": [
        (tkinter.Label(root, text="Render settings:"), 2, 0, 2, 1),
        (tkinter.Label(root, text="Video framerate:"), 2, 1, 1, 1), (tkinter.Entry(root, textvariable=framerate, validate='key', validatecommand=check_num_wrapper), 3, 1, 1, 1),
        (tkinter.Label(root, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tkinter.Entry(root, textvariable=bars, validate='key', validatecommand=check_num_wrapper), 3, 2, 1, 1),
        (tkinter.Label(root, text="Bar spacing (px):"), 2, 3, 1, 1), (tkinter.Entry(root, textvariable=bar_spacing, validate='key', validatecommand=check_num_wrapper), 3, 3, 1, 1),
        (tkinter.Label(root, text="Inbetween interpolation alpha:"), 2, 4, 1, 1), (tkinter.Entry(root, textvariable=lerp_alpha, validate='key', validatecommand=check_float_wrapper), 3, 4, 1, 1),
        (tkinter.Label(root, text="Interpolation rate:"), 2, 5, 1, 1), (tkinter.Entry(root, textvariable=lerp_speed, validate='key', validatecommand=check_float_wrapper), 3, 5, 1, 1),
        (tkinter.Label(root, text="Background image file:"), 2, 6, 1, 1), (OpenFileMenu(root, text="Select background...", targetvariable=background, filetypes=[('PNG image file', '*.png')], initialdir='/files'), 3, 6, 1, 1),
    ],
    "bars": [
        (tkinter.Label(root, text="Bar customization:"), 4, 0, 2, 1),
        (tkinter.Label(root, text="Screen coverage width:"), 4, 1, 1, 1), (tkinter.Entry(root, textvariable=coverage_x, validate='key', validatecommand=check_float_wrapper), 5, 1, 1, 1),
        (tkinter.Label(root, text="Screen coverage height:"), 4, 2, 1, 1), (tkinter.Entry(root, textvariable=coverage_y, validate='key', validatecommand=check_float_wrapper), 5, 2, 1, 1),
        (tkinter.Label(root, text="Horizontal justification (left-right):"), 4, 3, 1, 1), (tkinter.Entry(root, textvariable=bar_justify_x, validate='key', validatecommand=check_float_wrapper), 5, 3, 1, 1),
        (tkinter.Label(root, text="Vertical justification (top-bottom):"), 4, 4, 1, 1), (tkinter.Entry(root, textvariable=bar_justify_y, validate='key', validatecommand=check_float_wrapper), 5, 4, 1, 1),
        (tkinter.Label(root, text="Brightness exponent:"), 4, 5, 1, 1), (tkinter.Entry(root, textvariable=brightness_exp, validate='key', validatecommand=check_float_wrapper), 5, 5, 1, 1),
        (tkinter.Label(root, text="Height exponent:"), 4, 6, 1, 1), (tkinter.Entry(root, textvariable=height_exp, validate='key', validatecommand=check_float_wrapper), 5, 6, 1, 1),
    ],
    "presets": [
        (tkinter.Button(root, text="Save Preset", command=save_preset), 0, 7, 1, 1),
        (tkinter.Button(root, text="Load Preset", command=load_preset), 1, 7, 1, 1)
    ]
}

for category, elements in layout.items():
    widget_list[category] = []
    for widget, c, r, cs, rs in elements:
        sticky = None
        if isinstance(widget, tkinter.Label) and r > 0:
            sticky = 'e'
        if isinstance(widget, tkinter.Button) and r < 7:
            sticky = 'ew'
        widget.grid(sticky=sticky, column=c, row=r, columnspan=cs, rowspan=rs, padx=5, pady=5)
        widget_list[category].append(widget)

continue_button = tkinter.Button(root, text="Render")
continue_button.grid(column=2, row=7, columnspan=1, rowspan=1, padx=5, pady=5)

progress_bar = tkinter.ttk.Progressbar(root, orient="horizontal", mode="determinate", maximum=1)
progress_bar.grid(sticky='ew', column=0, row=8, columnspan=2, rowspan=3, padx=5, pady=5)
progress_label = tkinter.Label(root, text="Ready")
progress_label.grid(sticky='w', column=2, row=8, columnspan=3, rowspan=3, padx=5, pady=5)

def launch_ui():
    root.mainloop()