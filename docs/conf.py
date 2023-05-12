# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = "Data2RDF"
copyright = (
    "2023, Materials Data Science and " "Informatics Team at Fraunhofer IWM"
)
author = "Paul Zierep (Fraunhofer IWM)"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",  # markdown source support
    "sphinx.ext.autodoc",  # API ref
    "sphinx.ext.napoleon",  # API ref Google and NumPy style
    "sphinx.ext.viewcode",  # API link to source
    "sphinx.ext.graphviz",  # Graphviz
    "sphinx_copybutton",  # Copy button for codeblocks
    "nbsphinx",  # Jupyter
    "IPython.sphinxext.ipython_console_highlighting",  # nb syntax highlight
    "sphinx.ext.autosectionlabel",  # Auto-generate section labels.
    "sphinx_design",  # Create panels in a grid layout or as drop-downs
    "sphinxcontrib.redoc",  # Render OpenAPI with redoc
]

myst_enable_extensions = ["colon_fence"]
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_logo = "assets/img/logo.png"
html_favicon = "assets/img/favicon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["assets"]

# -- Options for LaTeX output -------------------------------------------------
latex_documents = [
    (
        "index",
        "data2rdf_docs.tex",
        "Data2RDF docs",
        ("Materials Data Science and " "Informatics team at Fraunhofer IWM"),
        "manual",
        "false",
    )
]
latex_logo = "assets/img/logo.png"
latex_elements = {"figure_align": "H"}

nbsphinx_allow_errors = True

suppress_warnings = ["myst.mathjax"]
