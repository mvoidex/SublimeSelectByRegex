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

class SelectNextRegex(sublime_plugin.TextCommand):
	def run(self, edit):
		self.text = self.view.substr(sublime.Region(0, self.view.size()))
		self.view.window().show_input_panel('regex', '', self.on_done, self.on_change, self.on_cancel)

	def on_done(self, rx):
		self.view.erase_regions('select next regex outer')
		self.view.erase_regions('select next regex inner')

		self.view.sel().clear()
		self.view.sel().add_all(self.inner_regions)

	def on_change(self, rx):
		self.in_group = has_in_group(rx)
		self.inner_regions = []
		self.outer_regions = []
		for r in self.view.sel():
			self.rx = re.compile(unwrap(rx, self.view.substr(r)), re.MULTILINE)
			m = self.rx.search(self.text, r.a)
			if m:
				if self.in_group:
					if 'Select' in m.groupdict():
						self.inner_regions.append(sublime.Region(m.start('Select'), m.end('Select')))
						self.outer_regions.append(sublime.Region(m.start(), m.end()))
				else:
					self.inner_regions.append(sublime.Region(m.start(), m.end()))
		self.view.add_regions('select next regex outer', self.outer_regions, 'string', '', sublime.DRAW_NO_FILL)
		self.view.add_regions('select next regex inner', self.inner_regions, 'string', '', sublime.DRAW_NO_OUTLINE)

	def on_cancel(self):
		self.view.erase_regions('select next regex outer')
		self.view.erase_regions('select next regex inner')

class SelectAllRegex(sublime_plugin.TextCommand):
	def run(self, edit):
		self.text = self.view.substr(sublime.Region(0, self.view.size()))
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

		rs = [r for r in self.view.sel() if not r.empty()]
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
