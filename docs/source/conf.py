import datetime

import sphinx_vhs

project = "Sphinx VHS"
copyright = f"{datetime.date.today().year}, Tamika Nomara"
author = "Tamika Nomara"
release = version = sphinx_vhs.__version__


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx_design",
    "sphinx_vhs",
]

templates_path = ["_templates"]
exclude_patterns = []
primary_domain = "py"
default_role = "py:obj"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "vhs": ("https://taminomara.github.io/python-vhs/", None),
}
autodoc_member_order = "bysource"
nitpick_ignore_regex = [(r"py:class", r".*\.T")]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/sphinx-contrib/vhs",
    "source_branch": "main",
    "source_directory": "docs/source",
}
