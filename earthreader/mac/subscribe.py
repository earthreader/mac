""":mod:`earthreader.mac.subscribe` --- Subscription list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from AppKit import NSTextField
from Foundation import NSObject
from libearth.subscribe import SubscriptionSet

__all__ = 'SubscriptionListModel',


class SubscriptionListModel(NSObject):
    """This is a delegate as well as a data source for NSOutlineViews."""

    def __new__(cls, stage):
        return cls.alloc().initWithStage_(stage)

    def initWithStage_(self, stage):
        self = self.init()
        self.stage = stage
        with stage:
            self.root = SubscriptionNode(stage.subscriptions, 0)
        return self

    # implements NSOutlineViewDataSource

    def outlineView_numberOfChildrenOfItem_(self, view, item):
        if item is None:
            item = self.root
        if self.outlineView_isItemExpandable_(view, item):
            return len(item.children)
        return 0

    def outlineView_child_ofItem_(self, view, child, item):
        if item is None:
            item = self.root
        return item.childAtIndex_(child)

    def outlineView_isGroupItem_(self, view, item):
        if item is None:
            return True
        return item.level < 1

    def outlineView_isItemExpandable_(self, view, item):
        if item is None:
            item = self.root
        return item.children is not None

    def outlineView_viewForTableColumn_item_(self, view, col, item):
        if item is None:
            item = self.root
        # FIXME: textField = view.makeViewWithIdentifier_owner_('Label', self)
        textField = NSTextField.alloc().init()
        textField.setStringValue_(str(item))
        textField.setEditable_(False)
        textField.setSelectable_(False)
        return textField


class SubscriptionNode(NSObject):
    """Wrapper class for items to be displayed in the outline view."""

    # We keep references to all child items (once created). This is
    # neccesary because NSOutlineView holds on to SubscriptionNode instances
    # without retaining them.  If we don't make sure they don't get
    # garbage collected, the app will crash.  For the same reason this
    # class _must_ derive from NSObject, since otherwise autoreleased
    # proxies will be fed to NSOutlineView, which will go away too soon.

    def __new__(cls, outline, level):
        return cls.alloc().initWithOutline_level_(outline, level)

    def initWithOutline_level_(self, outline, level):
        self = self.init()
        self.outline = outline
        self.level = level
        if isinstance(outline, SubscriptionSet):
            self.children = list(outline)
            self.children.sort(key=lambda o: o.label)
        else:
            self.children = None
        self._childRefs = {}
        return self

    def childAtIndex_(self, index):
        if index in self._childRefs:
            return self._childRefs[index]
        outline = self.children[index]
        node = type(self)(outline, self.level + 1)
        self._childRefs[index] = node
        return node

    def __str__(self):
        return self.outline.label
