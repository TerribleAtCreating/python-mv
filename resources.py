from import_modules import *

# Enumerations
class DialogFiletypes():
    png = ('PNG image file', '*.png')
    gif = ('GIF animated image file', '*.gif')
    json = ('JavaScript Object Notation file', '*.json')
    jsonPreset = ('JSON preset', '*.json')
    wav = ('Wave audio file', '*.wav')
    mp4 = ('MPEG-4 video file', '*.mp4')
    
BlendingModes = {
    "Additive": ImageChops.add,
    "Additive (unclipped)": ImageChops.add_modulo,
    "Subtractive": ImageChops.subtract,
    "Subtractive (unclipped)": ImageChops.subtract_modulo
}
ResolutionUpscale = {
    "No upscale": 0,
    "720p (SD)": 720,
    "1080p (HD)": 1080,
    "1440p (QHD)": 1440,
    "2160p (UHD - 4K)": 2160,
    "4320p (UHD - 8K)": 4320
}

# Formatting and typechecking functions
def assert_empty(text, context):
    if len(text) <= 0: raise ValueError(context + " is empty")
def assert_enum(value, enum, context):
    if not value in enum: raise ValueError(context + " is invalid (empty or outdated?)")
    
def format_path(path: str = os.curdir, initialdir: str = ''):
    return os.path.relpath(path, os.curdir + initialdir).replace("\\","/")

def check_num(newval):
    return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5
def check_float(newval):
    return re.match('^[+-]?(?:[0-9]*[.])?[0-9]*$', newval) is not None and len(newval) <= 5

# UI classes
def save_filename(filetypes, initialdir, formatInitial = False):
    filename = tkinter.filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=filetypes, initialdir=os.curdir+initialdir)
    if not filename: return ''
    return format_path(filename, initialdir if formatInitial else '')
def open_filename(filetypes, initialdir, formatInitial = False):
    filename = tkinter.filedialog.askopenfilename(filetypes=filetypes, defaultextension=filetypes, initialdir=os.curdir+initialdir)
    if not filename: return ''
    return format_path(filename, initialdir if formatInitial else '')

class OpenFileMenu(ttk.Button):
    def __init__(self, *args, filetypes, initialdir, variable: tk.StringVar, **kwargs):
        super().__init__(*args, command=lambda: variable.set(open_filename(filetypes, initialdir, True)), **kwargs)
        variable.trace_add('write', lambda *_: self.configure(text=variable.get() != '' and variable.get() or "No file selected"))
        
class SaveFileMenu(ttk.Button):
    def __init__(self, *args, filetypes, initialdir, variable: tk.StringVar, **kwargs):
        super().__init__(*args, command=lambda: variable.set(save_filename(filetypes, initialdir, True)), **kwargs)
        variable.trace_add('write', lambda *_: self.configure(text=variable.get() != '' and variable.get() or "No file selected"))
        
class Checkbox(ttk.Checkbutton):
    def __init__(self, *args, ontext=str(True), offtext=str(False), variable: tk.BooleanVar, **kwargs):
        button_command = lambda: self.configure(text=variable.get() and ontext or offtext)
        super().__init__(*args, variable=variable, command=button_command, onvalue=True, offvalue=False, **kwargs)
        button_command()
        variable.trace_add('write', lambda *_: button_command())

# Rendering resources
def to_signal_scale(signal):
    if signal < 1:
        signal = 1
    return math.log10(signal)