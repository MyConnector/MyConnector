# Configuration file for the Sphinx documentation builder.
#
# Copyright (C) 2014-2026 Evgeniy Korneechev <ek@myconnector.ru>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the version 2 of the GNU General
# Public License as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

project = "MyConnector"
copyright = "2014-2026, Evgeniy Korneechev <ek@myconnector.ru>"
author = "Evgeniy Korneechev"

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "rtd": ( "https://docs.readthedocs.io/en/stable/", None ),
    "python": ( "https://docs.python.org/3/", None ),
    "sphinx": ( "https://www.sphinx-doc.org/en/master/", None ),
}

intersphinx_disabled_domains = [ "std" ]

templates_path = [ "_templates" ]

epub_show_urls = "footnote"

html_theme = "sphinx_rtd_theme"

html_static_path = [ "_static" ]
