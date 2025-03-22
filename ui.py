from import_modules import *
from resources import *

currentVersion = "0.4.0"
app_id = u'terriac.pythonmv.main.040'
root = Tk()

root.title(f"Python-MV [{currentVersion}]")
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'mycompany.myproduct.subproduct.version')
root.iconphoto(True, PhotoImage(file="pymv.png"))

input_file = StringVar()
export_file = StringVar()
channel_pan = StringVar()

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
    "height_exp": .5,
    "watermark_toggle": True
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

channel_pan = StringVar(value=defaultpreset.get("channel_pan"))

framerate = StringVar(value=defaultpreset.get("framerate"))
bars = StringVar(value=defaultpreset.get("bars"))
bar_spacing = StringVar(value=defaultpreset.get("bar_spacing"))
lerp_alpha = StringVar(value=defaultpreset.get("lerp_alpha"))
lerp_speed = StringVar(value=defaultpreset.get("lerp_speed"))
background = StringVar(value=defaultpreset.get("background"))

coverage_x = StringVar(value=defaultpreset.get("coverage_x"))
coverage_y = StringVar(value=defaultpreset.get("coverage_y"))
bar_justify_x = StringVar(value=defaultpreset.get("bar_justify_x"))
bar_justify_y = StringVar(value=defaultpreset.get("bar_justify_y"))
brightness_exp = StringVar(value=defaultpreset.get("brightness_exp"))
height_exp = StringVar(value=defaultpreset.get("height_exp"))

watermark_file = StringVar(value=defaultpreset.get("watermark_file"))
watermark_toggle = BooleanVar(value=defaultpreset.get("watermark_toggle"))
watermark_blending = StringVar(value=defaultpreset.get("watermark_blending"))

check_num_wrapper = (root.register(check_num), '%P')
check_float_wrapper = (root.register(check_float), '%P')

# Dialog buttons
def save_preset():
    presetpath = save_filename([DialogFiletypes.jsonPreset], '/presets')
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
    presetpath = open_filename([DialogFiletypes.jsonPreset], '/presets')
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

tab_notebook = tkinter.Notebook(root)
main_tab = tkinter.Frame(tab_notebook) 
bar_tab = tkinter.Frame(tab_notebook)
watermark_tab = tkinter.Frame(tab_notebook)

tab_notebook.add(main_tab, text = "Main") 
tab_notebook.add(bar_tab, text = "Graphics")
tab_notebook.add(watermark_tab, text = "Watermark")
tab_notebook.grid(columnspan=4, rowspan=7)

widget_list = dict()
# Layout: [(Element, X, Y, Widthspan, Heightspan)]
layout = {
    "import/export": [
        (tkinter.Label(main_tab, text="Import/export settings"), 0, 0, 2, 1),
        (tkinter.Label(main_tab, text="Input file (.wav):"), 0, 1, 1, 1), (OpenFileMenu(main_tab, text="Select audio...", variable=input_file, filetypes=[DialogFiletypes.wav], initialdir='/files'), 1, 1, 1, 1),
        (tkinter.Label(main_tab, text="Export filename:"), 0, 2, 1, 1), (SaveFileMenu(main_tab, text="Select filename...", variable=export_file, filetypes=[DialogFiletypes.mp4], initialdir='/export'), 1, 2, 1, 1),
        (tkinter.Label(main_tab, text="Channel panning:"), 0, 3, 1, 1), (tkinter.Entry(main_tab, textvariable=channel_pan, validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
    ],
    "render": [
        (tkinter.Label(main_tab, text="Render settings"), 2, 0, 2, 1),
        (tkinter.Label(main_tab, text="Video framerate:"), 2, 1, 1, 1), (tkinter.Entry(main_tab, textvariable=framerate, validate='key', validatecommand=check_num_wrapper), 3, 1, 1, 1),
        (tkinter.Label(main_tab, text="Number of frequency bars to render:"), 2, 2, 1, 1), (tkinter.Entry(main_tab, textvariable=bars, validate='key', validatecommand=check_num_wrapper), 3, 2, 1, 1),
        (tkinter.Label(main_tab, text="Bar spacing (px):"), 2, 3, 1, 1), (tkinter.Entry(main_tab, textvariable=bar_spacing, validate='key', validatecommand=check_num_wrapper), 3, 3, 1, 1),
        (tkinter.Label(main_tab, text="Inbetween interpolation alpha:"), 2, 4, 1, 1), (tkinter.Entry(main_tab, textvariable=lerp_alpha, validate='key', validatecommand=check_float_wrapper), 3, 4, 1, 1),
        (tkinter.Label(main_tab, text="Interpolation rate:"), 2, 5, 1, 1), (tkinter.Entry(main_tab, textvariable=lerp_speed, validate='key', validatecommand=check_float_wrapper), 3, 5, 1, 1),
        (tkinter.Label(main_tab, text="Background image file:"), 2, 6, 1, 1), (OpenFileMenu(main_tab, text="Select background...", variable=background, filetypes=[DialogFiletypes.png], initialdir='/files'), 3, 6, 1, 1),
    ],
    "bars": [
        (tkinter.Label(bar_tab, text="Bar customization"), 0, 0, 2, 1),
        (tkinter.Label(bar_tab, text="Screen coverage width:"), 0, 1, 1, 1), (tkinter.Entry(bar_tab, textvariable=coverage_x, validate='key', validatecommand=check_float_wrapper), 1, 1, 1, 1),
        (tkinter.Label(bar_tab, text="Screen coverage height:"), 0, 2, 1, 1), (tkinter.Entry(bar_tab, textvariable=coverage_y, validate='key', validatecommand=check_float_wrapper), 1, 2, 1, 1),
        (tkinter.Label(bar_tab, text="Horizontal justification (left-right):"), 0, 3, 1, 1), (tkinter.Entry(bar_tab, textvariable=bar_justify_x, validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
        (tkinter.Label(bar_tab, text="Vertical justification (top-bottom):"), 0, 4, 1, 1), (tkinter.Entry(bar_tab, textvariable=bar_justify_y, validate='key', validatecommand=check_float_wrapper), 1, 4, 1, 1),
        (tkinter.Label(bar_tab, text="Brightness exponent:"), 0, 5, 1, 1), (tkinter.Entry(bar_tab, textvariable=brightness_exp, validate='key', validatecommand=check_float_wrapper), 1, 5, 1, 1),
        (tkinter.Label(bar_tab, text="Height exponent:"), 0, 6, 1, 1), (tkinter.Entry(bar_tab, textvariable=height_exp, validate='key', validatecommand=check_float_wrapper), 1, 6, 1, 1),
    ],
    "watermark": [
        (tkinter.Label(watermark_tab, text="Watermark settings"), 0, 0, 2, 1),
        (tkinter.Label(watermark_tab, text="Toggle watermark"), 0, 1, 1, 1), (Checkbox(watermark_tab, ontext="Enabled", offtext="Disabled", variable=watermark_toggle), 1, 1, 1, 1),
        (tkinter.Label(watermark_tab, text="Watermark image:"), 0, 2, 1, 1), (OpenFileMenu(watermark_tab, text="Select watermark...", variable=watermark_file, filetypes=[DialogFiletypes.png], initialdir='/files'), 1, 2, 1, 1),
        (tkinter.Label(watermark_tab, text="Watermark blending mode:"), 0, 3, 1, 1), (tkinter.OptionMenu(watermark_tab, watermark_blending, *BlendingModes.keys()), 1, 3, 1, 1),
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

progress_bar = tkinter.Progressbar(root, orient="horizontal", mode="determinate", maximum=1)
progress_bar.grid(sticky='ew', column=0, row=8, columnspan=2, rowspan=3, padx=5, pady=5)
progress_label = tkinter.Label(root, text="Ready")
progress_label.grid(sticky='w', column=2, row=8, columnspan=3, rowspan=3, padx=5, pady=5)

def check_version():
    latestVersion = requests.get("https://raw.githubusercontent.com/TerribleAtCreating/python-mv/main/version.txt", timeout=5).text.strip()
    if Version(currentVersion) < Version(latestVersion):
        if tkinter.messagebox.askyesno(
            "New release available: v" + latestVersion,
            "A new update for this script is available.\nWould you like to be directed to the release page?"):
                webbrowser.open("https://github.com/TerribleAtCreating/python-mv/releases", 2, True)

def launch_ui():
    threading.Thread(target=check_version).start()
    root.mainloop()