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
                    NSImage, NSNotificationCenter, NSSegmentedControl,
                    NSWindowController)
from Foundation import NSProcessInfo, NSThread, NSURL
from libearth.crawler import CrawlResult, crawl
from libearth.repository import FileSystemRepository
from libearth.session import Session
from libearth.stage import Stage
from objc import IBAction, IBOutlet
from Quartz import NSImageNameRefreshTemplate, NSImageNameStopProgressTemplate
from WebKit import WebView

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
        self.crawlTask = None
        # The window controller doesn't need to be retained (referenced)
        # anywhere, so we pretend to have a reference to ourselves to avoid
        # being garbage collected before the window is closed.  The extra
        # reference will be released in self.windowWillClose_().
        self.retain()
        return self

    def awakeFromNib(self):
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
        self.entryListView.mainFrame().windowObject().evaluateWebScript_(
            "document.body.classList.add('active')"
        )

    def applicationDidResignActive_(self, notification):
        self.entryListView.mainFrame().windowObject().evaluateWebScript_(
            "document.body.classList.remove('active')"
        )

    def windowWillClose_(self, notification):
        # see comment in self.initWithObject_()
        self.autorelease()

    def windowNibName(self):
        return 'MainWindow'

    def windowDidLoad(self):
        super().windowDidLoad()

    @IBAction
    def refreshWithSender_(self, sender):
        if self.crawlTask is not None:
            return self.stopRefreshWithSender_(sender)
        logger.debug('%r refreshWithSender:%r', self, sender)
        sender.setImage_(NSImage.imageNamed_(NSImageNameStopProgressTemplate))
        self.crawlTask = NSThread.alloc().initWithTarget_selector_object_(
            self, 'crawlWithSender:', sender
        )
        self.crawlTask.start()

    @IBAction
    def stopRefreshWithSender_(self, sender):
        logger.debug('%r stopRefreshWithSender:%r', self, sender)
        sender.setImage_(NSImage.imageNamed_(NSImageNameRefreshTemplate))
        self.crawlTask = None

    @IBAction
    def showAddSubscriptionDialogWithSender_(self, sender):
        pass

    @IBAction
    def setFilterWithSender_(self, sender: NSSegmentedControl):
        logger.debug('%r setFilterWithSender:%r', self, sender)
        logger.debug('%r selectedSegment => %r',
                     sender, sender.selectedSegment())

    def crawlWithSender_(self, sender):
        try:
            subs = self.subscriptions.recursive_subscriptions
            logger.debug('len(subs) = %d', len(subs))
            feeds_dict = {s.feed_uri: s for s in subs}
            cput_count = NSProcessInfo.processInfo().activeProcessorCount()
            logger.debug('len(feeds_dict) = %d', len(feeds_dict))
            for result in crawl(feeds_dict, cput_count):
                assert isinstance(result, CrawlResult)
                logger.info('Crawled %d entries from %s',
                            len(result.feed.entries), result.url)
                sub = feeds_dict[result.url]
                with self.stage:
                    if result.icon_url:
                        sub.icon_uri = result.icon_url
                        self.stage.subscriptions = self.subscriptions
                    self.stage.feeds[sub.feed_id] = result.feed
            logger.info('Finished crawling %d feeds', len(feeds_dict))
        except Exception as e:
            logger.exception(e)
        finally:
            self.pyobjc_performSelectorOnMainThread_withObject_(
                'stopRefreshWithSender:', sender
            )

    def renderSubscriptions(self):
        renderTemplate(self.entryListView, 'subscriptions.html',
                       subscriptions=self.subscriptions)


def renderTemplate(webView: WebView, name: str, **values):
    html = render_template(name, **values)
    frame = webView.mainFrame()
    baseUrl = NSURL.URLWithString_('file://' + os.path.dirname(__file__) +
                                   '/static/')
    frame.loadHTMLString_baseURL_(html, baseUrl)


def main():
    session_id = 'mac-{:x}'.format(uuid.getnode())
    session = Session(session_id)
    repository_path = os.path.join(
        os.environ['HOME'], 'Dropbox (Personal)', 'Earth Reader'
    )  # FIXME
    repository = FileSystemRepository(repository_path)  # FIXME
    stage = Stage(session, repository)
    app = NSApplication.sharedApplication()
    viewController = MainController(stage)
    viewController.showWindow_(viewController)
    NSApp.activateIgnoringOtherApps_(True)
    return app
