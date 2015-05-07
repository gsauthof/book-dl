E-Book Download Tool

2015, Georg Sauthoff <mail@georg.so>

## Example

    $ ./book-dl.py http://gutenberg.spiegel.de/musil/mannohne/mannohne.xml --out dl
    [..]
    INFO:root:Book written to: dl/mannohne.epub

## Rationale

`book-dl` converts html e-books into the [EPUB][epub] format.
EPUB is an open format that is supported by many [e-book
readers][er]. Currently, the tool understands the HTML-structure
of [Projekt Gutenberg-DE][gbde] books. Note that *Projekt
Gutenberg-DE* is not related to [Project Gutenberg][pg]. Project
Gutenberg already publishes its books in various formats on its
website, including e-book reader friendly formats like EPUB and
plain text.

## Tested platforms

- Linux ([Fedora][f] 21, x86-64)

### Dependencies

- [Python 3][p3] (e.g. 3.4.1)
- [lxml][lxml]

## License

[GPLv3+][gpl3]


[gpl3]:    http://www.gnu.org/copyleft/gpl.html
[lxml]:    http://lxml.de/
[p3]:      https://www.python.org/
[f]:       https://getfedora.org/
[epub]:    https://en.wikipedia.org/wiki/EPUB
[gbde]:    https://de.wikipedia.org/wiki/Projekt_Gutenberg-DE
[er]:      https://en.wikipedia.org/wiki/E-reader
[pg]:      https://en.wikipedia.org/wiki/Project_Gutenberg
