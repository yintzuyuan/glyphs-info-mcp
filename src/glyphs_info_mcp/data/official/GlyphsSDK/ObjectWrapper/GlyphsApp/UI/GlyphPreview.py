# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ["GlyphPreview"]

import traceback

from AppKit import NSView, NSColor, NSRectFill
from vanilla.vanillaBase import VanillaBaseObject
from GlyphsApp import GSLayer


class GSGlyphPreviewView(NSView):

	def setGlyph_(self, glyph):
		self._glyph = glyph

	def setDelegate_(self, delegate):
		self._delegate = delegate

	def drawRect_(self, rect):
		frame = self.bounds()
		NSColor.whiteColor().set()
		NSRectFill(frame)
		try:
			if self._glyph is not None:
				if isinstance(self._glyph, GSLayer):
					layer = self._glyph
				if layer:
					layer.drawInFrame_(frame)
		except:
			print(traceback.format_exc())

	def mouseDown_(self, event):
		try:
			if event.clickCount() == 2:
				if self._delegate.mouseDoubleDownCallBack:
					self._delegate.mouseDoubleDownCallBack(self)
				return
			if self._delegate.mouseDownCallBack:
				self._delegate.mouseDownCallBack(self)
		except:
			print(traceback.format_exc())

	def mouseUp_(self, event):
		try:
			if self._delegate.mouseUpCallBack:
				self._delegate.mouseUpCallBack(self)
		except:
			print(traceback.format_exc())


class GlyphPreview(VanillaBaseObject):
	"""
	A control that allows for showing a glyph

	GlyphPreview objects handle GSLayer

		from vanilla import FloatingWindow
		from GlyphsApp.UI import GlyphPreview
		class GlyphPreviewDemo(object):
			def __init__(self):
				self.title = "Glyph Preview"
				self.w = FloatingWindow((200, 200), self.title)
				layer = Glyphs.font.selectedLayers[0]
				self.w.Preview = GlyphPreview((0, 0, 0, 0), layer=layer)
				self.w.Preview.mouseDoubleDownCallBack = self.mouseDoubleDown
				self.w.open()
			def mouseDoubleDown(self, sender):
				print("Mouse Double Down")

		GlyphPreviewDemo()

	**posSize** Tuple of form *(left, top, width, height)* representing the position and size of the color well.

	**layer** A *GSLayer*. If *None* is given, the view will be empty.
	"""

	nsGlyphPreviewClass = GSGlyphPreviewView

	def __init__(self, posSize, layer=None):
		self.mouseDownCallBack = None
		self.mouseDoubleDownCallBack = None
		self.mouseUpCallBack = None
		self._setupView(self.nsGlyphPreviewClass, posSize)
		self._nsObject.setDelegate_(self)
		self._nsObject.setGlyph_(layer)

	@property
	def layer(self):
		return self._nsObject._layer

	@layer.setter
	def layer(self, value):
		self._nsObject._layer = value
		self._nsObject.setNeedsDisplay_(True)
