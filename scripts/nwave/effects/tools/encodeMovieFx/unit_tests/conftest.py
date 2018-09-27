# -*- coding: utf-8 -*-
"""DOCSTRING."""

import pytest
from nwave.effects.tools.encodeMovieFx.encodeMovieFx import Settings
from nwave.effects.tools.encodeMovieFx import encodeMovieFx


class ImageConverter(object):
    start_count = 0
    join_count = 0
    init_count = 0
    init_args = []

    def __init__(self, *args, **kwargs):
        ImageConverter.init_count += 1
        ImageConverter.init_args.append([args, kwargs])

    def start(self):
        ImageConverter.start_count += 1

    def join(self):
        ImageConverter.join_count += 1

    def reset(self):
        ImageConverter.start_count = 0
        ImageConverter.call_count = 0
        ImageConverter.init_count = 0
        ImageConverter.init_args = []


@pytest.fixture
def exr_files(tmpdir):
    """Create test exr files in a temporary directory."""
    exr_dir = tmpdir.mkdir('exr')
    exr_files = []
    file_count = 100
    for i in range(file_count):
        f = exr_dir.join('999_0010_test.{}.{}'.format(
            str(i).zfill(4),
            Settings.IN_IMAGE_EXTENSION
        ))
        f.write('')
        exr_files.append(str(f))
    for i in range(10):
        exr_dir.join(
            '999_0010_test.{}.wrong_extension'.format(str(i).zfill(4))
        )
        f.write('')

    yield exr_files


@pytest.fixture
def image_converter(mocker):
    """Mock the ImageConverter class."""
    mocker.patch.object(encodeMovieFx, 'ImageConverter', ImageConverter)
    yield ImageConverter
