# -*- coding: utf-8 -*-
"""DOCSTRING."""

import sys
import os

sys.path.insert(
    0,
    os.path.join(
        os.path.split(__file__)[0],
        '..'
    )
)

import unittest

from PyQt5 import QtWidgets

from View import View
from Model import Model
from Controller import Controller


class MailGeneratorTest(unittest.TestCase):

    def build(self):
        view = View()
        model = Model()
        controller = Controller(model, view)

        return controller, model, view

    def test_init(self):
        controller, model, view = self.build()

        self.assertIsNotNone(model.sender)
        self.assertIsNotNone(model.user_name)
        self.assertIsNotNone(model.project_name)

        self.assertEqual(model.sequence, 0)
        self.assertEqual(model.shot, 0)
        self.assertEqual(len(view.assets), 0)

    def test_getShot(self):
        controller, model, view = self.build()

        self.assertIsNone(controller._getShot(0, 0))
        self.assertIsNotNone(controller._getShot(240, 160))

    def test_updateSequenceShot(self):
        controller, model, view = self.build()
        controller._updateSequenceShot()

        self.assertEqual(len(view.assets), 0)

        model.sequence = 240
        model.shot = 160

        controller._updateSequenceShot()

        self.assertNotEqual(len(view.assets), 0)
        self.assertEqual(len(model.assets), 0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    unittest.main()
