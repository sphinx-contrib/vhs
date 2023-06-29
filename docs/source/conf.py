# -- Project information -----------------------------------------------------

project = "Sphinx VHS"
copyright = "2023, Tamika Nomara"
author = "Tamika Nomara"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinxcontrib.jquery",
    "sphinx_vhs",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "vhs": ("https://taminomara.github.io/python-vhs/", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
