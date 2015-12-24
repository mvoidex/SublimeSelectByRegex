import re
import sublime
import sublime_plugin

def has_in_group(rx):
	return '(!' in rx

def has_sel(rx):
	return '$_' in rx

def unwrap_in(rx):
	# Unwrap (!...) group, returns regex and flag if this group was found
	return rx.replace('(!', '(?P<Select>')

def unwrap_sel(rx, s):
	# Unwrap $_ with regex, that match str
	return rx.replace('$_', re.escape(s))

def unwrap(rx, s):
	# Unwrap both, 'unwrap_in' must be first
	return unwrap_sel(unwrap_in(rx), s)

class SelectRegexNext(sublime_plugin.TextCommand):
	def run(self, edit, regex = None, line = False):
		self.text = self.view.substr(sublime.Region(0, self.view.size()))
		self.selections = [r for r in self.view.sel()]
		self.line = line
		self.view.sel().clear()
		self.view.window().show_input_panel('regex', regex or '', self.on_done, self.on_change, self.on_cancel)

	def on_done(self, rx):
		self.view.erase_regions('select next regex outer')
		self.view.erase_regions('select next regex inner')

		self.view.sel().add_all(self.inner_regions)

	def on_change(self, rx):
		self.in_group = has_in_group(rx)
		self.inner_regions = []
		self.outer_regions = []
		self.highlight_regions = []
		for r in self.selections:
			(cur_line, cur_column) = self.view.rowcol(r.a)
			self.rx = re.compile(unwrap(rx, self.view.substr(r)), re.MULTILINE)
			m = self.rx.search(self.view.substr(self.view.line(r)) if self.line else self.text, cur_column if self.line else r.b)
			# get current point from regex position
			def get_point(p):
				return self.view.text_point(cur_line, p) if self.line else p
			if m:
				if self.in_group:
					if 'Select' in m.groupdict():
						self.inner_regions.append(sublime.Region(get_point(m.start('Select')), get_point(m.end('Select'))))
						self.outer_regions.append(sublime.Region(get_point(m.start()), get_point(m.end())))
				else:
					self.inner_regions.append(sublime.Region(get_point(m.start()), get_point(m.end())))
		self.view.add_regions('select next regex outer', self.outer_regions, 'string', '', sublime.DRAW_NO_FILL)
		self.view.add_regions('select next regex inner', self.inner_regions, 'string', '', sublime.DRAW_NO_OUTLINE)

	def on_cancel(self):
		self.view.erase_regions('select next regex outer')
		self.view.erase_regions('select next regex inner')
		self.view.sel().add_all(self.selections)

class SelectRegexAll(sublime_plugin.TextCommand):
	def run(self, edit):
		self.text = self.view.substr(sublime.Region(0, self.view.size()))
		self.selections = [r for r in self.view.sel()]
		self.view.sel().clear()
		self.view.window().show_input_panel('regex', '', self.on_done, self.on_change, self.on_cancel)

	def on_done(self, rx):
		self.view.erase_regions('select all regex outer')
		self.view.erase_regions('select all regex inner')

		self.view.sel().clear()
		self.view.sel().add_all(self.inner_regions)

	def on_change(self, rx):
		self.in_group = has_in_group(rx)
		self.rx = re.compile(unwrap_in(rx), re.MULTILINE)
		self.inner_regions = []
		self.outer_regions = []
		self.start = 0

		rs = [r for r in self.selections if not r.empty()]
		if rs: # Find in selections
			for r in rs:
				self.start = r.a
				while True:
					m = self.rx.search(self.text, self.start, r.b)
					if m and self.start != m.end():
						if self.in_group:
							if 'Select' in m.groupdict():
								self.inner_regions.append(sublime.Region(m.start('Select'), m.end('Select')))
								self.outer_regions.append(sublime.Region(m.start(), m.end()))
						else:
							self.inner_regions.append(sublime.Region(m.start(), m.end()))
						self.start = m.end()
					else:
						break
		else: # Find anywhere
			while True:
				m = self.rx.search(self.text, self.start)
				if m and self.start != m.end():
					if self.in_group:
						if 'Select' in m.groupdict():
							self.inner_regions.append(sublime.Region(m.start('Select'), m.end('Select')))
							self.outer_regions.append(sublime.Region(m.start(), m.end()))
					else:
						self.inner_regions.append(sublime.Region(m.start(), m.end()))
					self.start = m.end()
				else:
					break
		
		self.view.add_regions('select all regex outer', self.outer_regions, 'string', '', sublime.DRAW_NO_FILL)
		self.view.add_regions('select all regex inner', self.inner_regions, 'string', '', sublime.DRAW_NO_OUTLINE)

	def on_cancel(self):
		self.view.erase_regions('select all regex outer')
		self.view.erase_regions('select all regex inner')
		self.view.sel().add_all(self.selections)

class DropSelectRegexRegions(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		# view.erase_regions('select next regex highlight')
		pass
