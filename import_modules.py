try:
    import ffmpeg
    import numpy
    import matplotlib.pyplot as plt
    import PIL
    from PIL import Image, ImageDraw, ImageOps, ImageChops
except ImportError as error:
    print("Failed to import modules:", error)
    print("Import error! Please install any missing libraries, then restart the script.")
    quit()
    
from enum import Enum

import math
import json
import re

import wave

import tkinter; import tkinter.filedialog; import tkinter.messagebox
import tkinter.ttk

import os
import ctypes
import threading; from threading import Thread
import timeit