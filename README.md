# python-mv
A small Python script for rendering music videos with FFmpeg.
## Module dependencies
### FFmpeg
This script relies heavily on the FFmpeg library.
You can install it at https://www.ffmpeg.org/. Install it by adding it to your PATH values, and you're good to go!

### Python-specific modules
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
- [NumPy](https://numpy.org/)
- [Pillow](https://python-pillow.org/)
- [matplotlib](https://matplotlib.org/)

If you haven't installed these already, the script will exit before anything major is executed.

## Usage
### What do I use this for?
This tool is currently only used to render those moving bars you might see in some music videos.
You can add in a background image if you like, but I personally recommend using those screen images I made, just because it allows for more flexibility with most video editors.

It basically takes in audio, and gives you a video with all the visuals you would need.

### How do I use this?
- Install the release zip file and extract it.
- The "presets" folder is where your render settings (excluding audio and output names) are saved.
- The "files" folder is where you'll put your .wav and .png files for rendering.
- The "export" folder is where videos are rendered and saved.

Your background image should be 1600x900 or any downscale of it for that sweet 16:9 ratio.
- Open the python script using the "start.bat" file or via IDE
    - When asked for a file name, you must include the extension.

- Tip: Use "greenscreen.png" as the background image so that you can later edit it in as an overlay in a video editor
  - You can also use "redscreen.png" or "bluescreen.png" if your editor allows for those effects
  - You can also use "blackscreen.png" if your editor allows for color cutouts
  - Don't make a correct "whitescreen.png" file (because why would you do that it's going to blend in with the cool bars i gave you)

- Tip: Use the "quick" preset to render videos with the settings I use, aka the settings you may have seen on some of my showcases
  - (almost) equivalent to the preloaded settings

The bar fill color will be white and varies based off its relative height and the settings in use.