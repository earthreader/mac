import logging

from objc import setVerbose
from PyObjCTools import AppHelper

from earthreader.mac.log import NSLogHandler
from earthreader.mac.main import main


if __name__ == '__main__':
    handler = NSLogHandler()
    handler.setLevel(logging.DEBUG)  # FIXME
    for logger_name in 'earthreader', 'libearth':
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)  # FIXME
    main()
    setVerbose(1)
    AppHelper.runEventLoop()
