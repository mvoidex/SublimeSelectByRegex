import re
import sublime
import sublime_plugin


def used_sel(rx):
	return '$_' in rx


def unwrap_sel(rx, s):
	# Unwrap $_ with regex, that match str
	return rx.replace('$_', re.escape(s))


class SelectByRegexBase(sublime_plugin.TextCommand):

	# Add regions from regex match
	def mark_groups(self, match):
		if len(match.groups()):
			for number, group in list(enumerate(match.groups(), start=1)):
				self.inner_regions.append(sublime.Region(match.start(number), match.end(number)))
			self.outer_regions.append(sublime.Region(match.start(), match.end()))
		else:
			self.inner_regions.append(sublime.Region(match.start(), match.end()))
		self.active_view.sel().clear()

	# Mark found regions
	def mark_regions(self):
		self.focus()
		self.active_view.add_regions('select by regex: outer', self.outer_regions, 'string', '', sublime.DRAW_NO_FILL)
		self.active_view.add_regions('select by regex: inner', self.inner_regions, 'string', '', sublime.DRAW_NO_OUTLINE)

	# Focus view on first match
	def focus(self):
		if len(self.outer_regions):
			self.active_view.show(self.outer_regions[0])
		elif len(self.inner_regions):
			self.active_view.show(self.inner_regions[0])

	def erase_regions(self):
		self.active_view.erase_regions('select by regex: selections')
		self.active_view.erase_regions('select by regex: regions')
		self.active_view.erase_regions('select by regex: outer')
		self.active_view.erase_regions('select by regex: inner')
		self.active_view.settings().erase('select_by_regex_running')

	def on_done(self, rx):
		self.erase_regions()
		self.active_view.sel().add_all(self.inner_regions)

	def on_cancel(self):
		self.erase_regions()
		self.active_view.sel().add_all(self.selections)
		self.active_view.show(self.selections[0])


class SelectByRegexNext(SelectByRegexBase):

	is_running = False
	active_me = None

	def me(self):
		if SelectByRegexNext.is_running and SelectByRegexNext.active_me is not None:
			return SelectByRegexNext.active_me
		return self

	def run(self, edit, regex = None):
		if SelectByRegexNext.is_running:
			self.me().regions = self.me().active_view.get_regions('select by regex: regions')
			if regex:
				self.me().regex = regex
		else:
			self.regex = regex or ''
			self.active_view = self.view
			SelectByRegexNext.is_running = True
			self.selections = [r for r in self.active_view.sel()]
			self.regions = self.selections.copy()
			self.active_view.add_regions('select by regex: selections', self.selections, '', '', sublime.HIDDEN)
			SelectByRegexNext.active_me = self

		self.me().text = self.me().active_view.substr(sublime.Region(0, self.me().active_view.size()))
		self.me().active_view.sel().clear()
		self.me().active_view.window().show_input_panel(
			'regex',
			self.me().regex,
			self.me().on_done,
			self.me().on_change,
			self.me().on_cancel)
		if self.me().regex:
			print('REGEX: {0}'.format(self.me().regex))
			self.me().on_change(self.me().regex)

	def on_done(self, rx):
		super(SelectByRegexNext, self).on_done(rx)
		SelectByRegexNext.is_running = False

	def on_cancel(self):
		super(SelectByRegexNext, self).on_cancel()
		SelectByRegexNext.is_running = False

	def on_change(self, rx):
		print('CHANGE: {0}'.format(self.regions))
		self.regex = rx
		self.inner_regions = []
		self.outer_regions = []
		self.highlight_regions = []
		rest = []
		for r in self.regions:
			self.rx = re.compile(unwrap_sel(rx, self.active_view.substr(r)), re.MULTILINE)
			m = self.rx.search(self.text, r.end() if used_sel(rx) else r.begin())
			if m and (used_sel(rx) or r.empty() or m.end() <= r.end()):  # Restrict to selection if it's not empty
				self.mark_groups(m)
				if r.empty():
					rest.append(sublime.Region(m.end(), m.end()))
				else:
					rest.append(sublime.Region(m.end(), r.end()))
		self.active_view.add_regions('select by regex: regions', rest)
		self.mark_regions()


class SelectByRegexAll(SelectByRegexBase):

	def run(self, edit, regex = None):
		self.active_view = self.view
		self.selections = [r for r in self.active_view.sel()]
		self.active_view.add_regions('select by regex: selections', self.selections, '', '', sublime.HIDDEN)
		self.text = self.active_view.substr(sublime.Region(0, self.active_view.size()))
		self.active_view.sel().clear()
		self.active_view.window().show_input_panel(
			'regex',
			regex or '',
			self.on_done,
			self.on_change,
			self.on_cancel)

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
						self.mark_groups(m)
						self.start = m.end()
					else:
						break
		else:  # Find anywhere
			while True:
				m = self.rx.search(self.text, self.start)
				if m and self.start != m.end():
					self.mark_groups(m)
					self.start = m.end()
				else:
					break
		self.mark_regions()


class DropSelectByRegexRegions(sublime_plugin.EventListener):

	def on_selection_modified(self, view):
		pass
