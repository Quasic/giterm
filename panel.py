# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from collections import OrderedDict

class PanelManager(OrderedDict):
	def __init__(self, stdscr):
		super(PanelManager, self).__init__()
		self.stdscr = stdscr
		self.create_panels()

	def create_panels(self):
		"""Creates a SourceTree-like interface:
┌────────┐┌────────────────────────────────┐
│Branches││Log history                     │
│> master││                                │
│> devel ││                                │
│        ││                                │
│Remotes ││                                │
│> origin│└────────────────────────────────┘
│        │┌───────────────┐┌───────────────┐
│Tags    ││ Staged files  ││               │
│        │└───────────────┘│ Diff of       │
│Stashes │┌───────────────┐│ selected file │
│        ││ Changed files ││               │
└────────┘└───────────────┘└───────────────┘
		"""
		height, width = self.stdscr.getmaxyx()
		w_15_pct = width // 7
		w_30_pct = width // 3
		w_55_pct = width - w_30_pct - w_15_pct
		h_49_pct = height // 2
		h_51_pct = height - h_49_pct
		h_25_pct = h_51_pct // 2
		h_26_pct = h_51_pct - h_25_pct
		self['hier']    = Panel(self.stdscr, height, w_15_pct, 0, 0)
		self['loghist'] = Panel(self.stdscr, h_49_pct, w_30_pct+w_55_pct, 0, w_15_pct)
		self['stage']   = Panel(self.stdscr, h_25_pct, w_30_pct, h_49_pct, w_15_pct)
		self['changes'] = Panel(self.stdscr, h_26_pct, w_30_pct, h_49_pct+h_25_pct, w_15_pct)
		self['diff']    = Panel(self.stdscr, h_51_pct, w_55_pct, h_49_pct, w_15_pct+w_30_pct)

	def toggle(self):
		it = cycle(self.iteritems())
		for k, panel in it:
			if panel.active:
				panel.deactivate()
				return next(it)[1].activate()

	def display(self):
		active = None
		for k, panel in self.iteritems():
			panel.display()
			if panel.active:
				active = panel
		if active:
			self.stdscr.move(*active.getcontentyx())

class Panel(object):
	"""Encapsulates a window
	"""
	def __init__(self, stdscr, height, width, y, x, border='bounding'):
		self.content = []
		self.window = stdscr.derwin(height, width, y, x)
		self.border = border
		self.H, self.W = self.window.getmaxyx()
		self.T, self.L, self.B, self.R = 0, 0, height-1, width-1 # relative
		self.CNT_T, self.CNT_L, self.CNT_B, self.CNT_R = self.T+1, self.L+1, self.B-1, self.R-1
		self.middle = (self.H//2, self.W//2)
		self.abs_middle = ((self.H//2)+y-1, (self.W//2)+x-1)
		self.active = False
		self.selected = -1
		self.load_content()

	def display(self):
		self.window.clear()
		if self.active:
			self.window.box()
		else:
			self.window.border( ' ', ' ', ' ', ' ',
				curses.ACS_BSSB, curses.ACS_BBSS, curses.ACS_SSBB, curses.ACS_SBBS)
		for i in range(min(len(self.content), self.H-2)):
			y = i+self.CNT_T
			short = self.shorten(str(self.content[i]), self.W-3)
			self.window.addnstr(y, self.CNT_L, short, self.W-3)
			if y == self.selected:
				self.window.chgat(y, self.CNT_L, self.CNT_R, curses.A_REVERSE)
			# TODO: need to handle case of last line fulfilled with scrolling disabled
		self.window.move(self.selected if self.selected != -1 else self.CNT_T, self.CNT_L)
		self.window.refresh()

	def shorten(self, string, size):
		if len(string) > size:
			return string[:size-3] + '...'
		return string

	def load_content(self):
		for i in range(self.H-2):
			self.content.append("Content line #%s starts here and ends here." % str(i))

	# Callback function for remote observers
	def handle_event(self, event):
		self.content.insert(0, event.content)
		if self.selected != -1: self.selected += 1
		self.display()

	def select(self):
		y, x = self.window.getyx()
		self.selected = -1 if y == self.selected else y
		self.display()

	def activate(self):
		if self.active:
			return
		self.active = True
		self.display()
		return self

	def deactivate(self, force=False):
		if not self.active and not force:
			return
		self.active = False
		self.display()

	def getcontentyx(self):
		y, x = self.window.getbegyx()
		return y+self.CNT_T, x+self.CNT_L

	def text_center(self, row, col, string):
		self.window.addstr(row, col-len(string)/2, string)

	def text(self, y, x, string):
		self.window.addstr(y, x, string)

	def text_right_align(self, y, x, string):
		self.window.addstr(y, x-len(string)+1, string)

	def text_force_right_align(self, y, x, string):
		'''Forces right-aligned text to be printed
		until the last char position of the panel
		even with scrolling disabled''' 
		try:
			self.window.addstr(y, x-len(string)+1, string)
		except curses.error:
			pass

	def move_left(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_x > self.CNT_L:
			self.cursor_x -= 1
			self._move_cursor()

	def move_right(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_x < self.CNT_R:
			self.cursor_x += 1
			self._move_cursor()

	def move_up(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_y > self.CNT_T:
			self.cursor_y -= 1
			self._move_cursor()

	def move_down(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_y < self.CNT_B:
			self.cursor_y += 1
			self._move_cursor()

	def _move_cursor(self):
		self.window.move(self.cursor_y, self.cursor_x)
		self.window.refresh()

	def debug(self, refresh=True):
		self.window.box(curses.ACS_CKBOARD,curses.ACS_CKBOARD)
		active = '  Active  ' if self.active else ' Inactive '
		self.text_center(0, self.W//2, active)
		self.text_center(self.middle[0], self.middle[1], str(self.middle))
		size = '[' + str(self.H) + ' x ' + str(self.W) + ']'
		self.text_center(self.middle[0]+1, self.middle[1], size)
		TL = str((self.T, self.L))
		self.window.addstr(self.T, self.L, TL)
		TR = str((self.T, self.R))
		self.text_force_right_align(self.T, self.R, TR)
		BL = str((self.B, self.L))
		self.window.addstr(self.B, self.L, BL)
		BR = str((self.B, self.R))
		self.text_force_right_align(self.B, self.R, BR)
		if refresh:
			self.window.refresh()
