try:
    import ffmpeg
    import numpy
    import matplotlib.pyplot as plt
    import requests
    import webbrowser
    from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageSequence, ImageTk
except ImportError as error:
    print("Failed to import modules:", error)
    print("Import error! Please install any missing libraries, then restart the script.")
    quit()
    
from enum import Enum

import math
import json
import re

import wave

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog, tkinter.messagebox

import os
import traceback
import ctypes
import threading; from threading import Thread
import timeit
from packaging.version import Version