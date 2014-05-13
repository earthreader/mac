""":mod:`earthreader.mac.subscribe` --- Subscription list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from Foundation import NSObject
from libearth.stage import Stage
from libearth.subscribe import Outline, SubscriptionSet

__all__ = 'SubscriptionListModel', 'SubscriptionNode'


logger = logging.getLogger(__name__)


class SubscriptionNode(NSObject):
    """Wrapper class for items to be displayed in the outline view."""

    # We keep references to all child items (once created). This is
    # neccesary because NSOutlineView holds on to SubscriptionNode instances
    # without retaining them.  If we don't make sure they don't get
    # garbage collected, the app will crash.  For the same reason this
    # class _must_ derive from NSObject, since otherwise autoreleased
    # proxies will be fed to NSOutlineView, which will go away too soon.

    def __new__(cls, outline: Outline, level: int):
        return cls.alloc().initWithOutline_level_(outline, level)

    def initWithOutline_level_(self, outline: Outline, level: int):
        self = self.init()
        self.outline = outline
        self.level = level
        self.category = isinstance(outline, SubscriptionSet)
        if self.category:
            self.children = list(outline)
            self.children.sort(key=lambda o: o.label)
        else:
            self.children = None
        self._childRefs = {}
        return self

    def isCategory(self) -> bool:
        return self.category

    def childAtIndex_(self, index: int):
        if index in self._childRefs:
            return self._childRefs[index]
        outline = self.children[index]
        node = type(self)(outline, self.level + 1)
        self._childRefs[index] = node
        return node

    def __str__(self):
        return self.outline.label


class SubscriptionListModel(NSObject):
    """This is a delegate as well as a data source for NSOutlineViews."""

    def __new__(cls, stage: Stage):
        return cls.alloc().initWithStage_(stage)

    def initWithStage_(self, stage: Stage):
        self = self.init()
        self.stage = stage
        with stage:
            self.root = SubscriptionNode(stage.subscriptions, 0)
        return self

    # implements NSOutlineViewDataSource

    def outlineView_numberOfChildrenOfItem_(self, view,
                                            item: SubscriptionNode):
        if item is None:
            item = self.root
        if self.outlineView_isItemExpandable_(view, item):
            return len(item.children)
        return 0

    def outlineView_child_ofItem_(self, view, child,
                                  item: SubscriptionNode) -> SubscriptionNode:
        if item is None:
            item = self.root
        return item.childAtIndex_(child)

    def outlineView_isGroupItem_(self, view, item: SubscriptionNode) -> bool:
        if item is None:
            return True
        return item.level < 1

    def outlineView_isItemExpandable_(self, view,
                                      item: SubscriptionNode) -> bool:
        if item is None:
            item = self.root
        return item.children is not None

    def outlineView_viewForTableColumn_item_(self, view, col,
                                             item: SubscriptionNode):
        if item is None:
            item = self.root
        category = item.isCategory()
        cell = view.makeViewWithIdentifier_owner_(
            'HeaderCell' if category else 'DataCell',
            self
        )
        cell._.textField.setStringValue_(str(item))
        return cell
