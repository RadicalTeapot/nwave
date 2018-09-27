# -*- coding: utf-8 -*-
"""DOCSTRING."""

import os
import pytest
import shutil
import subprocess

from nwave.effects.tools.encodeMovieFx.encodeMovieFx import Settings
from nwave.effects.tools.encodeMovieFx.encodeMovieFx import EncodeMovieFx


class TestEncodeMovieFx:
    """Test suite for EncodeMovieFx class."""

    def test_init(self):
        """Test tool initialization."""
        encode_movie = EncodeMovieFx([])
        assert encode_movie.args == []
        assert encode_movie.path is None
        assert encode_movie.thread_count == Settings.DEFAULT_THREAD_COUNT
        assert encode_movie.production_name == Settings.DEFAULT_PROD_NAME
        assert encode_movie.in_folder is None
        assert encode_movie.out_folder is None
        assert encode_movie.filename is None
        assert encode_movie.current_frame is None
        assert encode_movie.seq_shot == Settings.DEFAULT_SEQ_SHOT
        assert encode_movie.title is None
        assert encode_movie.out_filepath is None
        assert encode_movie.username == os.environ['USERNAME']

    def test_arg_parser(self, mocker):
        """Test tool cli argument parsing."""
        # Test no args
        args = []
        encode_movie_fx = EncodeMovieFx(args)
        with pytest.raises(SystemExit) as e:
            encode_movie_fx.parse_args()
        assert e.value.code == 2

        # Test wrong args
        args = ['path/to/file.exr', '-w']
        encode_movie_fx = EncodeMovieFx(args)
        with pytest.raises(SystemExit) as e:
            encode_movie_fx.parse_args()
        assert e.value.code == 2

        # Test just path args
        args = ['999_0010_abc_beauty_v00_persp.0010.exr']
        encode_movie_fx = EncodeMovieFx(args)
        encode_movie_fx.parse_args()
        assert encode_movie_fx.path == args[0]

        # Test thread_count arg
        thread_count = 10
        args = [
            '999_0010_abc_beauty_v00_persp.0010.exr', '-c', str(thread_count)
        ]
        encode_movie_fx = EncodeMovieFx(args)
        encode_movie_fx.parse_args()
        assert encode_movie_fx.thread_count == thread_count

        # Test production_name arg
        prod_name = 'abc'
        args = [
            '999_0010_abc_beauty_v00_persp.0010.exr', '-p', prod_name
        ]
        encode_movie_fx = EncodeMovieFx(args)
        encode_movie_fx.parse_args()
        assert encode_movie_fx.production_name == prod_name

        # Test help flag
        args = [
            '999_0010_abc_beauty_v00_persp.0010.exr', '-h'
        ]
        encode_movie_fx = EncodeMovieFx(args)
        with pytest.raises(SystemExit) as e:
            encode_movie_fx.parse_args()
        assert e.value.code is None

    def test_filename_parser(self, mocker):
        """Test input file name parsing."""
        # Convinence function to run tests on parse_filename method
        def _run(args):
            encode_movie_fx = EncodeMovieFx(args)
            encode_movie_fx.parse_args()
            encode_movie_fx.parse_filename()
            return encode_movie_fx

        # Mock get_title_from_user to avoid raw_inputs calls
        raw_input_title = 'raw'
        patch = mocker.patch.object(
            EncodeMovieFx, 'get_title_from_user', return_value=raw_input_title
        )

        # Test invalid file extension
        args = ['path/to/999_0010_file.0010.jpg']
        with pytest.raises(SystemExit) as e:
            encode_movie_fx = _run(args)
        assert e.value.code == 1

        # Test missing frame number
        args = ['path/to/999_0010_file.exr']
        with pytest.raises(SystemExit) as e:
            encode_movie_fx = _run(args)
        assert e.value.code == 1

        # Test missing seq shot numbers
        args = ['path/to/file.0010.exr']
        encode_movie_fx = _run(args)
        assert encode_movie_fx.seq_shot == Settings.DEFAULT_SEQ_SHOT

        # Test seq shot number extraction
        seq_shot = '635_0120'
        args = ['path/to/{}_file.0010.exr'.format(seq_shot)]
        encode_movie_fx = _run(args)
        assert encode_movie_fx.seq_shot == seq_shot

        # Test title
        title = 'test'
        args = ['path/to/999_0010_{}.0010.exr'.format(title)]
        patch.reset_mock()
        encode_movie_fx = _run(args)
        assert encode_movie_fx.title == title
        assert not patch.called

        # Test no title
        title = 'test'
        args = ['path/to/999_0010.0010.exr'.format(title)]
        patch.reset_mock()
        encode_movie_fx = _run(args)
        assert encode_movie_fx.title == raw_input_title
        assert patch.called

        # Test titles to replace
        for title in Settings.TITLES_TO_REPLACE:
            args = ['path/to/999_0010_{}.0010.exr'.format(title)]
            patch.reset_mock()
            encode_movie_fx = _run(args)
            assert encode_movie_fx.title == raw_input_title
            assert patch.called

        # Test real file
        args = [
            (
                '/nwave/projects/CORGI/RENDER_3D/999/0010/test/high_res/'
                'mathiasc/masterLayer/beauty/v00/persp/a/'
                '999_0010_abc_beauty_v00_persp.0010.exr'
            )
        ]
        encode_movie_fx = _run(args)
        folder, filename = os.path.split(args[0])
        filename, _ = os.path.splitext(filename)
        filename, frame_num = filename.split('.')
        assert encode_movie_fx.in_folder == folder
        assert encode_movie_fx.out_folder == os.path.normpath(
            os.path.join(folder, Settings.TEMP_FOLDER)
        )
        assert encode_movie_fx.filename == filename
        assert encode_movie_fx.current_frame == frame_num
        assert encode_movie_fx.seq_shot == '999_0010'
        assert encode_movie_fx.title == 'abc'

    def test_get_image_list(self, exr_files):
        """Test getting input and output images."""
        encode_movie_fx = EncodeMovieFx([exr_files[0]])
        encode_movie_fx.parse_args()
        encode_movie_fx.parse_filename()
        in_images, out_images = encode_movie_fx.get_image_lists()
        # Test getting only images with correct extension
        assert len(in_images) == len(exr_files)
        # Test identical length for in and out lists
        assert len(in_images) == len(out_images)
        # Test output image extension
        assert os.path.splitext(os.path.split(out_images[0])[-1])[1] == \
            '.{}'.format(Settings.OUT_IMAGE_EXTENSION)
        # Test folders
        assert in_images[0].startswith(encode_movie_fx.in_folder)
        assert out_images[0].startswith(encode_movie_fx.out_folder)

    def test_split_into_buckets(self, exr_files):
        """Test splitting images into buckets."""
        # Convenience function to run tests
        def _run(args):
            encode_movie_fx = EncodeMovieFx(args)
            encode_movie_fx.parse_args()
            encode_movie_fx.parse_filename()
            in_images, _ = encode_movie_fx.get_image_lists()
            return encode_movie_fx.split_into_buckets(in_images)

        # Test normal case
        buckets = list(_run([exr_files[0]]))
        assert len(buckets) == EncodeMovieFx([]).thread_count

        # Test modified thread count
        thread_count = 10
        buckets = list(_run([exr_files[0], '-c', thread_count]))
        assert len(buckets) == thread_count

    def test_convert_images(self, exr_files, image_converter):
        """Test image type conversion and color correction."""
        encode_movie_fx = EncodeMovieFx([exr_files[0]])
        encode_movie_fx.parse_args()
        encode_movie_fx.parse_filename()
        encode_movie_fx.convert_images()

        # Test number of jobs started
        assert image_converter.init_count == Settings.DEFAULT_THREAD_COUNT
        assert image_converter.start_count == Settings.DEFAULT_THREAD_COUNT
        assert image_converter.join_count == Settings.DEFAULT_THREAD_COUNT

        # Test out_dir created
        assert os.path.exists(encode_movie_fx.out_folder)

        in_images, out_images = encode_movie_fx.get_image_lists()
        in_buckets = list(encode_movie_fx.split_into_buckets(in_images))
        out_buckets = list(encode_movie_fx.split_into_buckets(out_images))

        # Test call args vs bucket lengths
        assert len(image_converter.init_args) == len(in_buckets)
        assert len(image_converter.init_args) == len(out_buckets)

        for call_args, in_bucket, out_bucket in zip(
            image_converter.init_args,
            in_buckets,
            out_buckets
        ):
            args, kwargs = call_args
            # Test correct buckets assigned to jobs
            assert in_bucket in args
            assert out_bucket in args

    def test_generate_video(self, mocker):
        """Test generating video from files."""
        mocker.patch.object(
            EncodeMovieFx, 'get_title_from_user', return_value='test'
        )
        subprocess_mock = mocker.patch.object(subprocess, 'check_call')

        encode_movie_fx = EncodeMovieFx(['path/to/999_0010_file.0001.exr'])
        encode_movie_fx.parse_args()
        encode_movie_fx.parse_filename()
        encode_movie_fx.generate_video()

        # Test out_filepath
        assert encode_movie_fx.out_filepath.startswith(
            encode_movie_fx.in_folder
        )
        assert encode_movie_fx.filename in encode_movie_fx.out_filepath
        assert os.path.splitext(encode_movie_fx.out_filepath)[-1] == \
            '.{}'.format(Settings.OUT_VIDEO_EXTENSION)

        # Test function call
        assert subprocess_mock.called

        # Test args
        args = subprocess_mock.call_args[0][0]
        assert Settings.FFMPEG in args
        assert encode_movie_fx.current_frame in args
        assert Settings.FRAME_RATE in args
        assert Settings.CODEC in args
        assert Settings.BITRATE
        assert encode_movie_fx.out_filepath in args

    def test_run(self, mocker, exr_files, image_converter):
        """Test whole tool run operation."""
        mocker.patch.object(
            EncodeMovieFx, 'get_title_from_user', return_value='test'
        )
        mocker.patch.object(subprocess, 'check_call')
        subprocess_mocker = mocker.patch.object(subprocess, 'check_output')

        mocker.spy(EncodeMovieFx, 'parse_args')
        mocker.spy(EncodeMovieFx, 'parse_filename')
        mocker.spy(EncodeMovieFx, 'convert_images')
        mocker.spy(EncodeMovieFx, 'generate_video')
        mocker.spy(shutil, 'rmtree')

        encode_movie_fx = EncodeMovieFx([exr_files[0]])
        encode_movie_fx.run()

        # Test function calls
        assert encode_movie_fx.parse_args.called
        assert encode_movie_fx.parse_filename.called
        assert encode_movie_fx.convert_images.called
        assert encode_movie_fx.generate_video.called
        assert shutil.rmtree.called
        assert subprocess_mocker.called

        # Test arguments
        args = shutil.rmtree.call_args[0]
        assert encode_movie_fx.out_folder in args

        args = subprocess_mocker.call_args[0][0]
        assert Settings.LINUX_OPEN_FILE in args
        assert encode_movie_fx.out_filepath in args
