""":mod:`earthreader.mac.main` --- Main window
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import os
import os.path
import uuid

from AppKit import (NSApp, NSApplication,
                    NSApplicationDidBecomeActiveNotification,
                    NSApplicationDidResignActiveNotification,
                    NSNotificationCenter, NSSegmentedControl,
                    NSWindowController)
from Foundation import NSURL
from libearth.repository import FileSystemRepository
from libearth.session import Session
from libearth.stage import Stage
from objc import IBAction, IBOutlet
from WebKit import WebView  # noqa

from .tpl import render_template

__all__ = 'MainController',


logger = logging.getLogger(__name__)


class MainController(NSWindowController):

    entryListView = IBOutlet()
    contentView = IBOutlet()

    def __new__(cls, stage):
        return cls.alloc().initWithStage_(stage)

    def initWithStage_(self, stage):
        logger.debug('%r initWithStage_:%r', self, stage)
        self = self.init()
        self.stage = stage
        with stage:
            self.subscriptions = self.stage.subscriptions
        # The window controller doesn't need to be retained (referenced)
        # anywhere, so we pretend to have a reference to ourselves to avoid
        # being garbage collected before the window is closed.  The extra
        # reference will be released in self.windowWillClose_().
        self.retain()
        return self

    def awakeFromNib(self):
        logger.debug('%r awakeFromNib', self)
        self.renderSubscriptions()
        center = NSNotificationCenter.defaultCenter()
        center.addObserver_selector_name_object_(
            self, 'applicationDidBecomeActive:',
            NSApplicationDidBecomeActiveNotification,
            None
        )
        center.addObserver_selector_name_object_(
            self, 'applicationDidResignActive:',
            NSApplicationDidResignActiveNotification,
            None
        )

    def applicationDidBecomeActive_(self, notification):
        logger.debug('%r applicationDidBecomeActive:%r', self, notification)
        self.entryListView.mainFrame().windowObject().evaluateWebScript_(
            "document.body.classList.add('active')"
        )

    def applicationDidResignActive_(self, notification):
        logger.debug('%r applicationDidResignActive:%r', self, notification)
        self.entryListView.mainFrame().windowObject().evaluateWebScript_(
            "document.body.classList.remove('active')"
        )

    def windowWillClose_(self, notification):
        # see comment in self.initWithObject_()
        self.autorelease()
        logger.debug('%r windowWillClose:%r', self, notification)

    def windowNibName(self):
        return 'MainWindow'

    def windowDidLoad(self):
        super().windowDidLoad()

    @IBAction
    def refreshWithSender_(self, sender):
        pass

    @IBAction
    def showAddSubscriptionDialogWithSender_(self, sender):
        pass

    @IBAction
    def setFilterWithSender_(self, sender: NSSegmentedControl):
        logger.debug('%r setFilterWithSender:%r', self, sender)
        logger.debug('%r selectedSegment => %r',
                     sender, sender.selectedSegment())

    def renderSubscriptions(self):
        html = render_template('subscriptions.html',
                               subscriptions=self.subscriptions)
        frame = self.entryListView.mainFrame()
        baseUrl = NSURL.URLWithString_(
            'file://' + os.path.dirname(__file__) + '/static/'
        )
        frame.loadHTMLString_baseURL_(html, baseUrl)


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
