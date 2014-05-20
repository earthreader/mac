import logging
import os
import os.path

from Foundation import NSLog
from objc import setVerbose
from PyObjCTools import AppHelper

from earthreader.mac.log import NSLogHandler
from earthreader.mac.main import main


if __name__ == '__main__':
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    debug_handler = NSLogHandler()
    debug_handler.setLevel(logging.DEBUG)  # FIXME
    logfile_path = os.path.join(os.environ['HOME'], 'Library', 'Logs',
                                'EarthReader.log')
    file_handler = logging.FileHandler(logfile_path)
    file_handler.setLevel(logging.DEBUG)  # FIXME
    file_handler.setFormatter(formatter)
    for logger_name in 'earthreader', 'libearth':
        logger = logging.getLogger(logger_name)
        logger.addHandler(debug_handler)
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)  # FIXME
    NSLog('Logs will go to ' + logfile_path)
    main()
    setVerbose(1)
    AppHelper.runEventLoop()
