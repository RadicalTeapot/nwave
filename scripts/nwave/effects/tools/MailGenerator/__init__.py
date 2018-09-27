# -*- coding: utf-8 -*-
"""Build and send commit emails."""

import sys
import os
import platform

try:
    from PyQt5 import QtWidgets
except ImportError:
    if 'windows' in platform.system().lower():
        sys.path.insert(
            0,
            r"\\nwave\applications\external\libraries\PyQt5\winpython-py3.5.2"
        )
    else:
        sys.path.insert(
            0,
            "/nwave/applications/external/libraries/PyQt5/5.7.1-py3.5/linux64"
        )
        sys.path.insert(
            1,
            "/nwave/applications/external/libraries/sip/4.19-py3.5/linux64"
        )
finally:
    from PyQt5 import QtWidgets

sys.path.append(os.path.normpath(
    "//nwave/applications/internal/libraries/zefir/current_corgi"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/internal/libraries/zefiro/current_corgi"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/external/libraries/appdirs/1.4.0-py3.5"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/external/libraries/requests/2.5.3-py2.7"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/external/libraries/six/1.10.0-py3.5"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/external/libraries/pytz/2016.4-py3.5"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/external/libraries/natsort/4.0.4"
))
sys.path.append(os.path.normpath(
    "//nwave/applications/external/libraries/tzlocal/1.1.2-py3.5"
))

from Controller import Controller
from Model import Model
from View import View

if __name__ == '__main__':
    args = sys.argv
    args.append('--disable-web-security')  # This allows to load local images
    app = QtWidgets.QApplication(args)

    view = View()
    model = Model()
    Controller(model, view)

    view.show()

    sys.exit(app.exec_())
