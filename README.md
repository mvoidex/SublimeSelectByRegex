Select By Regex
==================

[![Package Control](https://packagecontrol.herokuapp.com/downloads/Select%20By%20Regex.svg?style=flat-square)](https://packagecontrol.io/packages/Select%20By%20Regex)

![Select](images/SelectAll.gif)

This plugin used to select by regex. Command `Select By Regex: All` selects all, `Select By Regex: Next` selects first found regex for each selection. If you want restrict search for line, use `Expand Selection to Line` before calling `Select By Regex` command.<br>
If regex contain groups, then groups will be select. To exclude group from selection use `(?:...)` group. `Select By Regex: Next` can also use `$_` to match string under current selection.

![Select All](images/SelectRegexAll.png)
![Select Next](images/SelectRegexNext.gif)

Bind to keys
---

You can use this keymap
<pre>
{
    "keys": ["ctrl+alt+f"],
    "command": "select_by_regex_next",
},
{
    "keys": ["ctrl+alt+a"],
    "command": "select_by_regex_all"
}
</pre>

