Select By Regex
==================

This plugin used to select by regex. Command `Select By Regex: All` selects all, `Select By Regex: Next` selects first found regex for each selection, `Select By Regex: Next (multiline)` is the same, but don't restrict search for line<br>
Regex can also contain special group `(!...)`, which used to mark group, which will be actually selected. If there are no such group, entire regex will be selected. `Select By Regex: Next` can also use `$_` to match string under current selection.

![Select All](SelectAllRegex.png)
![Select Next](SelectNextRegex.png)

Bind to keys
---

You can use this keymap
<pre>
{
    "keys": ["ctrl+alt+f"],
    "command": "select_by_regex_next",
    "args": { "line": true }
},
{
    "keys": ["ctrl+alt+shift+f"],
    "command": "select_by_regex_next"
},
{
    "keys": ["ctrl+alt+a"],
    "command": "select_by_regex_all"
}
</pre>

