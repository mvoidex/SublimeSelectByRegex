import re
import sublime
import sublime_plugin


def used_sel(rx):
	return '$_' in rx


def unwrap_sel(rx, s):
	# Unwrap $_ with regex, that match str
	return rx.replace('$_', re.escape(s))


class SelectByRegexBase(sublime_plugin.TextCommand):

	def run(self, edit, regex=None):
		self.text = self.view.substr(sublime.Region(0, self.view.size()))
		self.selections = [r for r in self.view.sel()]
		self.view.sel().clear()
		self.view.window().show_input_panel('regex', regex or '', self.on_done, self.on_change, self.on_cancel)

	def mark_groups(self, match):
		for number, group in list(enumerate(match.groups(), start=1)):
			self.inner_regions.append(sublime.Region(match.start(number), match.end(number)))
		self.outer_regions.append(sublime.Region(match.start(), match.end()))


class SelectByRegexNext(SelectByRegexBase):

	def on_done(self, rx):
		self.view.erase_regions('select by regex, next, outer')
		self.view.erase_regions('select by regex, next, inner')

		self.view.sel().add_all(self.inner_regions)

	def on_change(self, rx):
		self.inner_regions = []
		self.outer_regions = []
		self.highlight_regions = []
		for r in self.selections:
			self.rx = re.compile(unwrap_sel(rx, self.view.substr(r)), re.MULTILINE)
			m = self.rx.search(self.text, r.end() if used_sel(rx) else r.begin())
			if m and (used_sel(rx) or r.empty() or m.end() < r.end()):  # Restrict to selection if it's not empty
				if len(m.groups()) > 0:
					self.mark_groups(m)
				else:
					self.inner_regions.append(sublime.Region(m.start(), m.end()))
		self.view.add_regions('select by regex, next, outer', self.outer_regions, 'string', '', sublime.DRAW_NO_FILL)
		self.view.add_regions('select by regex, next, inner', self.inner_regions, 'string', '', sublime.DRAW_NO_OUTLINE)

	def on_cancel(self):
		self.view.erase_regions('select by regex, next, outer')
		self.view.erase_regions('select by regex, next, inner')
		self.view.sel().add_all(self.selections)


class SelectByRegexAll(SelectByRegexBase):

	def on_done(self, rx):
		self.view.erase_regions('select by regex, all, outer')
		self.view.erase_regions('select by regex, all, inner')

		self.view.sel().clear()
		self.view.sel().add_all(self.inner_regions)

	def on_change(self, rx):
		self.rx = re.compile(rx, re.MULTILINE)
		self.inner_regions = []
		self.outer_regions = []
		self.start = 0

		rs = [r for r in self.selections if not r.empty()]
		if rs:  # Find in selections
			for r in rs:
				self.start = r.begin()
				while True:
					m = self.rx.search(self.text, self.start, r.end())
					if m and self.start != m.end():
						if len(m.groups()) > 0:
							self.mark_groups(m)
						else:
							self.inner_regions.append(sublime.Region(m.start(), m.end()))
						self.start = m.end()
					else:
						break
		else:  # Find anywhere
			while True:
				m = self.rx.search(self.text, self.start)
				if m and self.start != m.end():
					if len(m.groups()) > 0:
						self.mark_groups(m)
					else:
						self.inner_regions.append(sublime.Region(m.start(), m.end()))
					self.start = m.end()
				else:
					break

		self.view.add_regions('select by regex, all, outer', self.outer_regions, 'string', '', sublime.DRAW_NO_FILL)
		self.view.add_regions('select by regex, all, inner', self.inner_regions, 'string', '', sublime.DRAW_NO_OUTLINE)

	def on_cancel(self):
		self.view.erase_regions('select by regex, all, outer')
		self.view.erase_regions('select by regex, all, inner')
		self.view.sel().add_all(self.selections)


class DropSelectByRegexRegions(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		# view.erase_regions('select by regex, next, highlight')
		pass
