""":mod:`earthreader.mac.log` --- ``NSLog`` adapter for stdlib :mod:`logging`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from Foundation import NSLog

__all__ = 'NSLogHandler',


class NSLogHandler(logging.Handler):

    def emit(self, record):
        NSLog(self.format(record))
