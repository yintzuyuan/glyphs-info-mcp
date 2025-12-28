# encoding: utf-8

from __future__ import absolute_import
from Cocoa import NSMenuItem
from .GlyphView import GlyphView
from .CanvasView import CanvasView
from .GlyphPreview import GlyphPreview

__all__ = ["GlyphView", "CanvasView", "GlyphPreview", "SteppingEditText", "MenuItem"]

try:
	from vanilla import EditText
except:
	EditText = object
from Foundation import NSClassFromString


class SteppingEditText(EditText):
	nsTextFieldClass = NSClassFromString("GSSteppingTextField")


def MenuItem(title, action=None, target=None, keyboard="", modifier=0):
	item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, keyboard)
	item.setTarget_(target)
	return item
