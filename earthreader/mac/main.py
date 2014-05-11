""":mod:`earthreader.mac.main` --- Main window
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import os
import os.path
import uuid

from AppKit import NSApp, NSApplication, NSWindowController
from libearth.repository import FileSystemRepository
from libearth.session import Session
from libearth.stage import Stage
from objc import IBAction, IBOutlet
from WebKit import WebView  # noqa

from .subscribe import SubscriptionListModel

__all__ = 'EarthReaderController',


logger = logging.getLogger(__name__)


class MainController(NSWindowController):

    subscriptionListView = IBOutlet()
    entryListView = IBOutlet()
    contentView = IBOutlet()

    def __new__(cls, stage):
        return cls.alloc().initWithStage_(stage)

    def initWithStage_(self, stage):
        logger.debug('%r initWithStage_:%r', self, stage)
        self = self.init()
        self.stage = stage
        self.subscriptionListModel = SubscriptionListModel(stage)
        # The window controller doesn't need to be retained (referenced)
        # anywhere, so we pretend to have a reference to ourselves to avoid
        # being garbage collected before the window is closed.  The extra
        # reference will be released in self.windowWillClose_().
        self.retain()
        return self

    def awakeFromNib(self):
        logger.debug('%r awakeFromNib', self)
        sidebar = self.subscriptionListView
        sidebar.setDataSource_(self.subscriptionListModel)
        sidebar.setDelegate_(self.subscriptionListModel)

    def windowWillClose_(self, notification):
        # see comment in self.initWithObject_()
        self.autorelease()

    def windowNibName(self):
        return 'MainWindow'

    def windowDidLoad(self):
        super().windowDidLoad()

    @IBAction
    def hello_(self, sender):
        pass


def main():
    session_id = 'mac-{:x}'.format(uuid.getnode())
    session = Session(session_id)
    repository_path = os.path.join(os.environ['HOME'],
                                   'Dropbox', 'Earth Reader')  # FIXME
    repository = FileSystemRepository(repository_path)  # FIXME
    stage = Stage(session, repository)
    app = NSApplication.sharedApplication()
    viewController = MainController(stage)
    viewController.showWindow_(viewController)
    NSApp.activateIgnoringOtherApps_(True)
    return app
