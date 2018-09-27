#!/usr/bin/python

# -*- coding: utf-8 -*-
"""DOCSTRING."""

import os
import platform
import sys
import subprocess
import re
import shutil
import threading
import itertools
import getopt


class Settings:
    """Collection of variables used by the tool."""

    # ####################################################################### #
    #                                  CLI                                    #
    # ####################################################################### #
    DEFAULT_PROD_NAME = "Corgi"
    DEFAULT_THREAD_COUNT = 50

    THREAD_COUNT_FLAG = ('-c', '--thread_count')
    PROD_NAME_FLAG = ('-p', '--production_name')
    HELP_FLAG = '-h'

    # ####################################################################### #
    #                                 FFMPEG                                  #
    # ####################################################################### #
    _WIN_FFMPEG = "//nwave/software/FFmpeg/3.4.1/win64/bin/ffmpeg.exe"
    _UNIX_FFMPEG = "//nwave/software/FFmpeg/3.4.1/linux64/ffmpeg"
    FFMPEG = {
        'windows': _WIN_FFMPEG,
        'linux': _UNIX_FFMPEG
    }[platform.system().lower()]

    FONT_NORMAL = "//nwave/data/effects/_internal/fonts/arial.ttf"
    FONT_BOLD = "//nwave/data/effects/_internal/fonts/arialbd.ttf"

    OUT_VIDEO_EXTENSION = 'mov'
    FRAME_RATE = '24'
    CODEC = 'mjpeg'
    BITRATE = '96000K'

    # ####################################################################### #
    #                                  OCIO                                   #
    # ####################################################################### #
    _WIN_OCIO_LIB = '//nwave/software/OpenImageIO/1.5.22/win64/lib'
    _UNIX_OCIO_LIB = (
        '//nwave/software/OpenColorIO/1.0.9/linux64/lib:'
        '//nwave/software/OpenImageIO/1.8.6/linux64/lib64'
    )
    OCIO_LIB = {
        'windows': _WIN_OCIO_LIB,
        'linux': _UNIX_OCIO_LIB,
    }[platform.system().lower()]

    _WIN_OCIOCONVERT = \
        "//nwave/software/OpenImageIO/1.5.22/win64/bin/ocioconvert.exe"
    _UNIX_OCIOCONVERT = \
        "//nwave/software/OpenColorIO/1.0.9/linux64/bin/ocioconvert"
    OCIO_CONVERT = {
        'windows': _WIN_OCIOCONVERT,
        'linux': _UNIX_OCIOCONVERT,
    }[platform.system().lower()]

    OCIO_CONFIG = "//NWAVE/DATA/color/aces_1.0.3-nwave/config.ocio"
    OCIO_IN_PROFILE = "ACES - ACEScg"
    OCIO_OUT_PROFILE = "Output - sRGB (D60 sim.)"

    TEMP_FOLDER = 'TEMP'
    DEFAULT_SEQ_SHOT = '000_0000'
    IN_IMAGE_EXTENSION = 'exr'
    OUT_IMAGE_EXTENSION = 'png'
    TITLES_TO_REPLACE = ['masterlayer']
    LINUX_OPEN_FILE = 'xdg-open'


class ImageConverter(threading.Thread):
    """Thread dedicated to image conversion and color correction."""

    def __init__(self, lock, in_images, out_images):
        """Initialize the thread.

        Parameters
        ----------
        lock: threading.Lock
            A lock used when printing data to main thread.
        in_images: list of str
            Paths to images to convert.
        out_images: list of str
            Paths to output converted images.

        """
        super(ImageConverter, self).__init__()
        self.lock = lock
        self.in_images = in_images
        self.out_images = out_images

    def run(self):
        """Convert the images."""
        # Create a file descriptor to devnull
        with open(os.devnull, 'w') as dev_null:
            for in_image, out_image in zip(self.in_images, self.out_images):
                if in_image is None or out_image is None:
                    continue
                # Pipe all messages to devnull to suppress them
                subprocess.check_call(
                    [
                        Settings.OCIO_CONVERT,
                        in_image, Settings.OCIO_IN_PROFILE,
                        out_image, Settings.OCIO_OUT_PROFILE
                    ],
                    stdout=dev_null,
                    stderr=dev_null
                )
                # Lock before printing to avoid multiple print on the same
                # line
                self.lock.acquire(1)
                print '{} converted'.format(in_image)
                self.lock.release()


def ffmpeg_draw_box(
    text, bold=False, size=10, pos=(0, 0), anchor=('right', 'top'), extra=[]
):
    """Draw a box on the frame with the given data.

    Parameters
    ----------
    text: str
        The text to put in the box
    bold: bool
        Whether the text should be in bold font.
    size: int
        The size of the text's font.
    pos: tuple of 2 int
        The position relative to the anchor.
    anchor: tuple of 2 str
        Where to place the text box relative to the image. Valid values are
        'left' or 'right' for the first value and 'top' or 'bottom' for the
        second value.
    extra: list of str
        Extra flags to pass to the command.

    """
    x = '{}{:+.0f}'.format(
        '' if anchor[0] == 'left' else 'w-text_w',
        pos[0] if anchor[0] == 'left' else pos[0] * -1
    )
    y = '{}{:+.0f}'.format(
        '' if anchor[1] == 'top' else 'h-text_h',
        pos[1] if anchor[1] == 'top' else pos[1] * -1
    )
    return (
        "drawtext="
        "fontfile={font}:"
        "fontcolor=white:"
        "fontsize={size}:"
        "box=1:"
        "boxcolor=DarkGray:"
        "boxborderw=5:"
        "{extra}"
        "text='{text}':"
        "x={x}:"
        "y={y}"
    ).format(
        font=Settings.FONT_BOLD if bold else Settings.FONT_NORMAL,
        size=size,
        extra=':'.join(extra) + ':' if extra else '',
        text=text,
        x=x, y=y,
    )


class EncodeMovieFx(object):
    """Convert a folder of images to a color corrected video."""

    # The text printed if incorrect arguments are passed to the cli
    cli_usage = (
        'usage: '
        'encodeMovieFx.py '
        'path/to/first_file_to_convert '
        '[-c/--thread_count thread_count] '
        '[-p/--production_name production_name] '
        '[-h]'
    )

    def __init__(self, args):
        """Initialize tool.

        Parameters
        -----------
        args: list of str
            The cli args passed to the script without the script name
            (i.e. sys.argv[1:]).

        """
        # Update the environement for ocio
        if 'windows' in platform.system().lower():
            os.environ['PATH'] += Settings.OCIO_LIB
        else:
            os.environ['LD_LIBRARY_PATH'] = Settings.OCIO_LIB
        os.environ["OCIO"] = Settings.OCIO_CONFIG

        self.args = args
        self.path = None
        self.thread_count = Settings.DEFAULT_THREAD_COUNT
        self.production_name = Settings.DEFAULT_PROD_NAME
        self.in_folder = None
        self.out_folder = None
        self.filename = None
        self.current_frame = None
        self.seq_shot = Settings.DEFAULT_SEQ_SHOT
        self.title = None
        self.out_filepath = None
        self.username = os.environ['USERNAME']

    def run(self):
        """Parse args and filename, convert images and generate video."""
        # Parse command line
        self.parse_args()
        # Parse input filename
        self.parse_filename()

        # Convert input images
        self.convert_images()
        # Generate video
        self.generate_video()

        # Delete temp folder
        shutil.rmtree(self.out_folder)

        # Open the video
        if self.out_filepath:
            if 'windows' in platform.system().lower():
                os.startfile(self.out_filepath)
            else:
                subprocess.check_output(
                    [Settings.LINUX_OPEN_FILE, self.out_filepath]
                )

    def parse_args(self):
        """Parse the command line args.

        Sets the path, thread_count, production_name vars.
        """
        if not self.args:
            print EncodeMovieFx.cli_usage
            sys.exit(2)

        self.path = self.args[0]
        if len(self.args) > 1:
            try:
                options, args = getopt.getopt(
                    self.args[1:],
                    '{help}{thread_count}:{prod_name}:'.format(
                        help=Settings.HELP_FLAG[1:],
                        thread_count=Settings.THREAD_COUNT_FLAG[0][1:],
                        prod_name=Settings.PROD_NAME_FLAG[0][1:]
                    ),
                    [
                        '{}='.format(Settings.THREAD_COUNT_FLAG[1][2:]),
                        '{}='.format(Settings.PROD_NAME_FLAG[1][2:])
                    ]
                )
            except getopt.GetoptError:
                print EncodeMovieFx.cli_usage
                sys.exit(2)

            for flag, argument in options:
                if flag == Settings.HELP_FLAG:
                    print EncodeMovieFx.cli_usage
                    sys.exit()
                elif flag in Settings.THREAD_COUNT_FLAG:
                    self.thread_count = int(argument)
                elif flag in Settings.PROD_NAME_FLAG:
                    self.production_name = argument

    def parse_filename(self):
        """Parse the given filepath.

        Sets the in_folder, out_folder, filename, current_frame, seq_shot and
        title vars.
        """
        clean_path = os.path.normpath(os.path.abspath(self.path))
        # Extract path to the folder
        self.in_folder, filename = os.path.split(clean_path)

        # Build output folder
        self.out_folder = os.path.normpath(
            os.path.join(self.in_folder, Settings.TEMP_FOLDER)
        )

        filename, extension = os.path.splitext(filename)
        if not re.compile('.+?\.[0-9]{4,4}').match(filename):
            print (
                'Wrong file name formatting, should be filename.frame_num.{}.'
            ).format(Settings.IN_IMAGE_EXTENSION)
            sys.exit(1)
        # Extract filename and extension
        self.filename, self.current_frame = filename.split('.')
        # Check for correct file extension
        if extension not in '.{}'.format(Settings.IN_IMAGE_EXTENSION):
            print 'Wrong input file type, should be {}.'.format(
                Settings.IN_IMAGE_EXTENSION
            )
            sys.exit(1)

        # Get seq and shot info from filename
        seq_shot_pattern = re.compile("[0-9]{3,}_[0-9]{4,}")
        result = seq_shot_pattern.findall(self.filename)
        if result:
            self.seq_shot = result[0]

        # Get title from filename
        split_name = self.filename.split('_')
        if len(split_name) > 2:
            self.title = split_name[2]
        # Get title from user when it is masterlayer
        if not self.title or self.title.lower() in Settings.TITLES_TO_REPLACE:
            self.title = self.get_title_from_user()

    def get_title_from_user(self):
        """Get title from raw input.

        Returns
        -------
        str
            The title.

        """
        return raw_input("Contents : ").strip()

    def get_image_lists(self):
        """Build and return lists of input and output images.

        Returns
        -------
        list, list
            The paths to input and output images.

        """
        in_images = []
        out_images = []
        files = [
            f
            for f in os.listdir(self.in_folder)
            if Settings.IN_IMAGE_EXTENSION in f
        ]
        for name in files:
            name, _ = os.path.splitext(name)
            in_images.append(os.path.normpath(os.path.join(
                self.in_folder,
                '{}.{}'.format(name, Settings.IN_IMAGE_EXTENSION))
            ))
            out_images.append(os.path.normpath(os.path.join(
                self.out_folder,
                '{}.{}'.format(name, Settings.OUT_IMAGE_EXTENSION))
            ))
        return in_images, out_images

    def split_into_buckets(self, images):
        """Split given image list into buckets.

        The number of buckets (length of the returned iterator) is equal to the
        thread count, the missing elements are filled with None (i.e if
        thread_count = 3 and images = range(10) then
        buckets = [[0, 3, 6, 9], [1, 4, 7, None], [2, 5, 8, None]]).

        Parameters
        ----------
        images: list of str
            The list of images to split

        Returns
        -------
        iterator of list of str
            The bucket list iterator.

        """
        return itertools.izip_longest(
            *(
                images[i:i + self.thread_count]
                for i in xrange(0, len(images), self.thread_count)
            )
        )

    def convert_images(self):
        """Convert input exr image to color corrected png images."""
        # Get image lists
        in_images, out_images = self.get_image_lists()

        # Get buckets
        in_buckets = self.split_into_buckets(in_images)
        out_buckets = self.split_into_buckets(out_images)

        # Create conversion jobs
        lock = threading.Lock()
        jobs = []
        for in_bucket, out_bucket in zip(in_buckets, out_buckets):
            jobs.append(ImageConverter(lock, in_bucket, out_bucket))

        # Create output folder if it doesn't exist
        if not os.path.exists(self.out_folder):
            os.makedirs(self.out_folder)

        # Launch the jobs
        for job in jobs:
            job.start()

        # Wait for all jobs to terminate
        for job in jobs:
            job.join()

    def generate_video(self):
        """Generate mov video file from png files."""
        # Build file path for ffmpeg
        in_filepath = os.path.join(
            self.out_folder,
            "{filename}.%{padding}d.{extension}".format(
                filename=self.filename,
                padding=len(self.current_frame),
                extension=Settings.OUT_IMAGE_EXTENSION
            )
        )

        # Movie path
        self.out_filepath = os.path.join(
            self.in_folder,
            "{}.{}".format(self.filename, Settings.OUT_VIDEO_EXTENSION)
        )

        print 'Generating video...'
        # Generate video
        subprocess.check_call([
            Settings.FFMPEG,

            "-hide_banner",                         # Reduce log verbose
            "-loglevel", "panic",                   # Reduce log verbose

            "-start_number", self.current_frame,    # Set first frame
            "-r", Settings.FRAME_RATE,              # Set video frame rate
            "-f", "image2",                         # Set input codec to image
            "-i", in_filepath,                      # Set input path

            "-vf",                                  # Draw ui
            ', '.join([
                ffmpeg_draw_box(
                    'Production\\: {}'.format(self.production_name),
                    bold=True, size=12, pos=(15, 10)
                ),
                ffmpeg_draw_box(
                    'Shot\\: {}'.format(self.seq_shot), pos=(15, 53)
                ),
                ffmpeg_draw_box(
                    'Date %{localtime\\:%d-%m-%Y}', pos=(15, 75)
                ),
                ffmpeg_draw_box(
                    'Content\\: {}'.format(self.title), pos=(15, 97)
                ),
                ffmpeg_draw_box(
                    'Artist\\: {}'.format(self.username), pos=(15, 119)
                ),
                ffmpeg_draw_box(
                    '%{frame_num}',
                    bold=True, size=14, pos=(15, 10),
                    anchor=('right', 'bottom'),
                    extra=['start_number={}'.format(self.current_frame)]
                ),
            ]),

            "-vcodec", Settings.CODEC,              # Set output codec
            "-b:v", Settings.BITRATE,               # Set bitrate

            "-y", self.out_filepath,                # Set output path
        ])


if __name__ == '__main__':
    EncodeMovieFx(sys.argv[1:]).run()
