from import_modules import *

# Enumerations
class DialogFiletypes(Enum):
    png = ('PNG image file', '*.png')
    json = ('JavaScript Object Notation file', '*.json')
    jsonPreset = ('JSON preset', '*.json')
    wav = ('Wave audio file', '*.wav')
    mp4 = ('MPEG-4 video file', '*.mp4')

# General functions
def multiple_function(*args):
    for func in args: func()

# Formatting and typechecking functions
def assert_empty(text, context):
    if len(text) <= 0: raise ValueError(context + " is empty")
def format_path(path: str = os.curdir, initialdir: str = ''):
    return os.path.relpath(path, os.curdir + initialdir).replace("\\","/")

def check_num(newval):
    return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5
def check_float(newval):
    return re.match('^[+-]?(?:[0-9]*[.])?[0-9]*$', newval) is not None and len(newval) <= 5

# UI classes
def save_filename(filetypes, initialdir, formatInitial = False):
    filename = tkinter.filedialog.asksaveasfilename(filetypes=filetypes, initialdir=os.curdir+initialdir)
    if not filename: return ''
    return format_path(filename, initialdir if formatInitial else '')
def open_filename(filetypes, initialdir, formatInitial = False):
    filename = tkinter.filedialog.askopenfilename(filetypes=filetypes, initialdir=os.curdir+initialdir)
    if not filename: return ''
    return format_path(filename, initialdir if formatInitial else '')

class OpenFileMenu(tkinter.Button):
    def __init__(self, *args, filetypes, initialdir, targetvariable: tkinter.StringVar, **kwargs):
        super().__init__(*args, command=lambda:
            multiple_function(
                lambda: targetvariable.set(open_filename(filetypes, initialdir, True)),
                lambda: self.configure(text=targetvariable.get() != '' and targetvariable.get() or "No file selected")
            ), **kwargs)
class SaveFileMenu(tkinter.Button):
    def __init__(self, *args, filetypes, initialdir, targetvariable: tkinter.StringVar, **kwargs):
        super().__init__(*args, command=lambda: multiple_function(
                lambda: targetvariable.set(save_filename(filetypes, initialdir, True)),
                lambda: self.configure(text=targetvariable.get() != '' and targetvariable.get() or "No file selected")
            ), **kwargs)

# Rendering resources
def to_signal_scale(signal):
    if signal < 1:
        signal = 1
    return 20 * math.log10(signal)