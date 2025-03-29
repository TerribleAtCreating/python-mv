from import_modules import *
from resources import *

currentVersion = "0.4.1"
versionStatus = ", indev"
app_id = u'terriac.pythonmv.main.040'
root = tk.Tk()

root.title(f"Python-MV [{currentVersion + versionStatus}]")
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
root.iconphoto(True, tk.PhotoImage(file="pymv.png"))

"""
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
"""

default_values = {
    "video_upscale": 0,
    
    "channel_pan": .5,
    "bar_orientation": False,
    
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
    "watermark_size": .5,
    "watermark_toggle": False,
    "watermark_blending": "Additive"
}

session_variables = {
    "input_file": tk.StringVar(root),
    "export_file": tk.StringVar(root),
    "video_upscale": tk.StringVar(root)
}

preset_variables = {
    "channel_pan": tk.DoubleVar(root),
    "bar_orientation": tk.BooleanVar(root),

    "framerate": tk.IntVar(root),
    "bars": tk.IntVar(root),
    "bar_spacing": tk.IntVar(root),
    "lerp_alpha": tk.DoubleVar(root),
    "lerp_speed": tk.DoubleVar(root),
    "background": tk.StringVar(root),

    "coverage_x": tk.DoubleVar(root),
    "coverage_y": tk.DoubleVar(root),
    "bar_justify_x": tk.DoubleVar(root),
    "bar_justify_y": tk.DoubleVar(root),
    "brightness_exp": tk.DoubleVar(root),
    "height_exp": tk.DoubleVar(root),

    "watermark_file": tk.StringVar(root),
    "watermark_size": tk.DoubleVar(root),
    "watermark_toggle": tk.BooleanVar(root),
    "watermark_blending": tk.StringVar(root)
}

for name, value in default_values.items():
    if name in session_variables:
        session_variables[name].set(value)
    if name in preset_variables:
        preset_variables[name].set(value)
        
# User variable functions
def get_variable(name):
    if name in session_variables:
        return session_variables[name]
    if name in preset_variables:
        return preset_variables[name]
    
    print(f"Provided variable name {name} is invalid.")
    
def get_value(name):
    variable = get_variable(name)
    if variable:
        return variable.get()

def set_variable(name, value):
    variable = get_variable(name)
    if variable:
        return variable.set(value)

check_num_wrapper = (root.register(check_num), '%P')
check_float_wrapper = (root.register(check_float), '%P')

# Dialog buttons
def save_preset():
    presetpath = save_filename([DialogFiletypes.jsonPreset], '/presets')
    if not presetpath: return
    with open(presetpath, 'w') as jsonoutput:
        preset_json = {}
        for name, variable in preset_variables.items():
            preset_json[name] = variable.get()
        json.dump(preset_json, jsonoutput)
def load_preset():
    presetpath = open_filename([DialogFiletypes.jsonPreset], '/presets')
    if not presetpath: return
    if not os.path.isfile(presetpath):
        ttk.messagebox.showwarning("File not found", "Selected file does not exist.")
        return
    preset: dict = json.load(open(presetpath))
    
    for name, value in preset.items():
        set_variable(name, value)

tab_notebook = ttk.Notebook(root)
main_tab = ttk.Frame(tab_notebook) 
bar_tab = ttk.Frame(tab_notebook)
watermark_tab = ttk.Frame(tab_notebook)

tab_notebook.add(main_tab, text = "Main") 
tab_notebook.add(bar_tab, text = "Graphics")
tab_notebook.add(watermark_tab, text = "Watermark")
tab_notebook.grid(columnspan=4, rowspan=7)

widget_list = dict()

# Layout definition: [(Element, X, Y, Widthspan, Heightspan)]
layout = {
    "label": [
        (ttk.Label(main_tab, text="Import/export settings"), 0, 0, 2, 1),
        (ttk.Label(main_tab, text="Input file (.wav):"), 0, 1, 1, 1),
        (ttk.Label(main_tab, text="Export filename:"), 0, 2, 1, 1),
        (ttk.Label(main_tab, text="Channel panning:"), 0, 3, 1, 1),
        (ttk.Label(main_tab, text="Video upscale:"), 0, 4, 1, 1),
        (ttk.Label(main_tab, text="Bar orientation"), 0, 5, 1, 1),
        
        (ttk.Label(main_tab, text="Render settings"), 2, 0, 2, 1),
        (ttk.Label(main_tab, text="Video framerate:"), 2, 1, 1, 1),
        (ttk.Label(main_tab, text="Number of frequency bars to render:"), 2, 2, 1, 1),
        (ttk.Label(main_tab, text="Bar spacing (px):"), 2, 3, 1, 1),
        (ttk.Label(main_tab, text="Inbetween interpolation alpha:"), 2, 4, 1, 1),
        (ttk.Label(main_tab, text="Interpolation rate:"), 2, 5, 1, 1), 
        (ttk.Label(main_tab, text="Background image file:"), 2, 6, 1, 1),
        
        (ttk.Label(bar_tab, text="Bar customization"), 0, 0, 2, 1),
        (ttk.Label(bar_tab, text="Screen coverage width:"), 0, 1, 1, 1),
        (ttk.Label(bar_tab, text="Screen coverage height:"), 0, 2, 1, 1),
        (ttk.Label(bar_tab, text="Horizontal justification (left-right):"), 0, 3, 1, 1),
        (ttk.Label(bar_tab, text="Vertical justification (top-bottom):"), 0, 4, 1, 1),
        (ttk.Label(bar_tab, text="Brightness exponent:"), 0, 5, 1, 1),
        (ttk.Label(bar_tab, text="Height exponent:"), 0, 6, 1, 1),
        
        (ttk.Label(watermark_tab, text="Watermark settings"), 0, 0, 2, 1),
        (ttk.Label(watermark_tab, text="Toggle watermark"), 0, 1, 1, 1),
        (ttk.Label(watermark_tab, text="Watermark image:"), 0, 2, 1, 1),
        (ttk.Label(watermark_tab, text="Watermark size (0-1):"), 0, 3, 1, 1),
        (ttk.Label(watermark_tab, text="Watermark blending mode:"), 0, 4, 1, 1)
    ],
    "render": [
        # Import/export
        (OpenFileMenu(main_tab, text="Select audio...", variable=get_variable("input_file"), filetypes=[DialogFiletypes.wav], initialdir='/files'), 1, 1, 1, 1),
        (SaveFileMenu(main_tab, text="Select filename...", variable=get_variable("export_file"), filetypes=[DialogFiletypes.mp4], initialdir='/export'), 1, 2, 1, 1),
        (ttk.Entry(main_tab, textvariable=get_variable("channel_pan"), validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
        (ttk.OptionMenu(main_tab, get_variable("video_upscale"), "Select upscale target...", *ResolutionUpscale.keys()), 1, 4, 1, 1),
        (Checkbox(main_tab, ontext="Vertical", offtext="Horizontal", variable=get_variable("bar_orientation")), 1, 5, 1, 1),

        # Render settings
        (ttk.Entry(main_tab, textvariable=get_variable("framerate"), validate='key', validatecommand=check_num_wrapper), 3, 1, 1, 1),
        (ttk.Entry(main_tab, textvariable=get_variable("bars"), validate='key', validatecommand=check_num_wrapper), 3, 2, 1, 1),
        (ttk.Entry(main_tab, textvariable=get_variable("bar_spacing"), validate='key', validatecommand=check_num_wrapper), 3, 3, 1, 1),
        (ttk.Entry(main_tab, textvariable=get_variable("lerp_alpha"), validate='key', validatecommand=check_float_wrapper), 3, 4, 1, 1),
        (ttk.Entry(main_tab, textvariable=get_variable("lerp_speed"), validate='key', validatecommand=check_float_wrapper), 3, 5, 1, 1),
        (OpenFileMenu(main_tab, text="Select background...", variable=get_variable("background"), filetypes=[DialogFiletypes.png], initialdir='/files'), 3, 6, 1, 1),
    
        # Graphics settings
        (ttk.Entry(bar_tab, textvariable=get_variable("coverage_x"), validate='key', validatecommand=check_float_wrapper), 1, 1, 1, 1),
        (ttk.Entry(bar_tab, textvariable=get_variable("coverage_y"), validate='key', validatecommand=check_float_wrapper), 1, 2, 1, 1),
        (ttk.Entry(bar_tab, textvariable=get_variable("bar_justify_x"), validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
        (ttk.Entry(bar_tab, textvariable=get_variable("bar_justify_y"), validate='key', validatecommand=check_float_wrapper), 1, 4, 1, 1),
        (ttk.Entry(bar_tab, textvariable=get_variable("brightness_exp"), validate='key', validatecommand=check_float_wrapper), 1, 5, 1, 1),
        (ttk.Entry(bar_tab, textvariable=get_variable("height_exp"), validate='key', validatecommand=check_float_wrapper), 1, 6, 1, 1),
    
        # Watermark
        (Checkbox(watermark_tab, ontext="Enabled", offtext="Disabled", variable=get_variable("watermark_toggle")), 1, 1, 1, 1),
        (OpenFileMenu(watermark_tab, text="Select watermark...", variable=get_variable("watermark_file"), filetypes=[DialogFiletypes.png], initialdir='/files'), 1, 2, 1, 1),
        (ttk.Entry(watermark_tab, textvariable=get_variable("watermark_size"), validate='key', validatecommand=check_float_wrapper), 1, 3, 1, 1),
        (ttk.OptionMenu(watermark_tab, get_variable("watermark_blending"), "Select blending mode...", *BlendingModes.keys()), 1, 4, 1, 1),
    ]
}

def initialize_widget(widget: ttk.Widget, x, y, width=1, height=1, sticky=None, category='uncategorized'):
    if not category in widget_list:
        widget_list[category] = []
    widget.grid(sticky=sticky, column=x, row=y, columnspan=width, rowspan=height, padx=5, pady=5)
    widget_list[category].append(widget)

max_row = 0
# Loop once to find max row (lowest row before untabbed widgets)
# This allows for a variable named "max_row" to be calculated,
# allowing for later widgets to be on a "seperate" grid
for _, elements in layout.items():        
    for _, _, row, _, _ in elements:
        max_row = max(max_row, row)
        
max_row += 1
 
# Loop again to initialize widgets  
for category, elements in layout.items():        
    for widget, c, r, cs, rs in elements:
        sticky = None
        if isinstance(widget, ttk.Label) and r > 0:
            sticky = 'e'
        if isinstance(widget, ttk.Button) and r < max_row:
            sticky = 'ew'
        initialize_widget(widget, c, r, cs, rs, sticky, category)

# Control widgets
continue_button = ttk.Button(root, text="Render")
initialize_widget(continue_button, 2, max_row + 0, category="controls")
preview_button = ttk.Button(root, text="Preview")
initialize_widget(preview_button, 3, max_row + 0, category="controls")
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", maximum=1)
initialize_widget(progress_bar, 0, max_row + 1, 4, 1, 'ew', category="controls")
progress_label = ttk.Label(root, text="Ready")
initialize_widget(progress_label, 0, max_row + 2, 4, 1, 'w', category="controls")

initialize_widget(ttk.Button(root, text="Save Preset", command=save_preset), 0, max_row + 0, 1, 1)
initialize_widget(ttk.Button(root, text="Load Preset", command=load_preset), 1, max_row + 0, 1, 1)

def check_version():
    # Get the latest version from a text file on GitHub
    latestVersion = requests.get("https://raw.githubusercontent.com/TerribleAtCreating/python-mv/main/version.txt", timeout=5).text.strip()
    
    # Use versioning to compare versions
    if Version(currentVersion) < Version(latestVersion):
        # Open a dialog asking to update
        if ttk.messagebox.askyesno(
            "New release available: v" + latestVersion,
            "A new update for this script is available.\nWould you like to be directed to the release page?"):
                webbrowser.open("https://github.com/TerribleAtCreating/python-mv/releases/latest", 2, True)

# Have this function be initialized in the main thread
def launch_ui():
    threading.Thread(target=check_version).start()
    root.mainloop()
    
def set_ui_state(newstate='normal'):
    for widget in widget_list['render']:
        widget.configure(state=newstate)