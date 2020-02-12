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
import datetime
import os
import sys
sys.path.insert(0, os.path.abspath('../../backend/'))


# -- Project information -----------------------------------------------------

project = 'Data Tracker'
copyright = f'2019-{datetime.datetime.now().year}, SciLifeLab Data Centre'
author = 'SciLifeLab Data Centre'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'recommonmark'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

html_logo = '_static/data-centre-logo.png'

html_theme_options = {
    'badge_branch': 'develop',
    'codecov_button': True,
    'github_banner': True,
    'github_button': False,
    'github_count': False,
    'github_repo': 'SciLifeLab-Data-Tracker',
    'github_user': 'ScilifelabDataCentre',
    'link': '#045C64',
    'link_hover': '#A7C947',
    'logo_name': True,
    'page_width': '1000px',
    'sidebar_width': '220px',
    'travis_button': True
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------
