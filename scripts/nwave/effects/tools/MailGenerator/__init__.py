# -*- coding: utf-8 -*-
"""Build and send commit emails."""

import sys
sys.path.insert(
    0, r"\\nwave\applications\external\libraries\PyQt5\winpython-py3.5.2"
)
sys.path.append(
    r"\\nwave\applications\internal\libraries\zefir\current_corgi"
)
sys.path.append(
    r"\\nwave\applications\internal\libraries\zefiro\current_corgi"
)
sys.path.append(
    r"\\nwave\applications\external\libraries\appdirs\1.4.0-py3.5"
)
sys.path.append(
    r"\\nwave\applications\external\libraries\requests\2.5.3-py2.7"
)
sys.path.append(
    r"\\nwave\applications\external\libraries\six\1.10.0-py3.5"
)
sys.path.append(
    r"\\nwave\applications\external\libraries\pytz\2016.4-py3.5"
)
sys.path.append(
    r"\\nwave\applications\external\libraries\natsort\4.0.4"
)
sys.path.append(
    r"\\nwave\applications\external\libraries\tzlocal\1.1.2-py3.5"
)

from Controller import Controller
from Model import Model
from View import View

from PyQt5 import QtWidgets

import sys


if __name__ == '__main__':
    args = sys.argv
    args.append('--disable-web-security')  # This allows to load local images
    app = QtWidgets.QApplication(args)

    view = View()
    model = Model()
    Controller(model, view)

    view.show()

    sys.exit(app.exec_())
