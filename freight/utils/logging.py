from __future__ import absolute_import

import logging

from blessings import Terminal


class ColoredFormatter(logging.Formatter):
    term = Terminal()

    colors = {
        'WARNING': term.yellow,
        'INFO': term.cyan,
        'DEBUG': term.white,
        'ERROR': term.red,
        'CRITICAL': term.bold_red,
    }

    def format(self, record):
        message = super(ColoredFormatter, self).format(record)
        func = self.colors[record.levelname]
        return func(message)
