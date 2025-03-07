try:
    import ffmpeg
    import numpy
    import matplotlib.pyplot as plt
    from PIL import Image
    from PIL import ImageDraw
except ImportError as error:
    print("Failed to import modules:", error)
    print("Import error! Please install any missing libraries, then restart the script.")
    quit()
    
import math
import json
import tkinter; import tkinter.filedialog; import tkinter.messagebox
import tkinter.ttk
import wave
import re
import os
import ctypes
import threading; from threading import Thread
import timeit