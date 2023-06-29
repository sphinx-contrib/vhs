Sphinx plugin for VHS
=====================

Sphinx-VHS is an integration plugin for Sphinx and VHS_,
a tool by charm_ that renders terminal commands into GIFs.
It allows referencing ``.tape`` files form your docs,
and rendering them during sphinx build.

.. _VHS: https://github.com/charmbracelet/vhs

.. _charm: https://charm.sh/

Quickstart
----------

Install the ``sphinx-vhs`` package:

.. code-block:: sh

    pip3 install sphinx-vhs

And add it to your ``conf.py``:

.. code-block:: python

   extensions = ["sphinx_vhs", ...]

Now put some tapes into your documentation source dir,
and use the **vhs** directive to render them:

.. code-block:: rst

   .. vhs:: _tapes/simple.tape
      :alt: A gif showing some hello-world text being typed into console.
      :scale: 25%

This will make you a nice gif:

.. highlights::

   .. vhs:: _tapes/simple.tape
      :alt: A gif showing some hello-world text being typed into console.
      :scale: 25%

Oh, and don't forget to compile with ``SPHINXOPTS="-j auto"`` to speed things up.
Sphinx-VHS can process tapes in parallel, but only if you let it.

Usage
-----

The **vhs** directive has all the same attributes as the figure_,
so you can caption it and reference it:

.. _figure: https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure

.. code-block:: rst

   .. _gif-reference:

   .. vhs:: _tapes/simple.tape
      :alt: A gif showing some hello-world text being typed into console.
      :scale: 25%

      Look, a small :ref:`gif <gif-reference>`! Isn't it cute?

This will make you a :ref:`figure <gif-reference>` with a caption:

.. highlights::

   .. _gif-reference:

   .. vhs:: _tapes/simple.tape
      :alt: A gif showing some hello-world text being typed into console.
      :scale: 25%

      Look, a small :ref:`gif <gif-reference>`! Isn't it cute?


There's also **vhs-inline**, which lets you paste a small tape right
into your documentation. It also works like a figure_,
but, well, you won't be able to caption it:

.. code-block:: rst

   .. vhs-inline::
      :scale: 25%

      Type "pwd"
      Sleep 500ms
      Enter
      Sleep 500ms
      Type "ls -l"
      Sleep 500ms
      Enter
      Sleep 5s

.. highlights::

   .. vhs-inline::
      :scale: 25%

      Type "pwd"
      Sleep 500ms
      Enter
      Sleep 500ms
      Type "ls -l"
      Sleep 500ms
      Enter
      Sleep 5s

Settings
--------

Sphinx-VHS adds the following settings to ``conf.py``:

- ``vhs_min_version``: minimum VHS version required to render types.

  Default: ``"0.5.0"``.

- ``vhs_cwd``: working dir for VHS runs.

  Default: documentation source dir.

- ``vhs_auto_install``: whether to install VHS in case it is missing or outdated.

  Default: ``True``.

- ``vhs_auto_install_location``: path where VHS binaries should be installed to.

  Default: see :func:`vhs.default_cache_path`.

But can it run inside ReadTheDocs?
----------------------------------

Nope! ReadTheDocs seems to use an older version of Linux core, which VHS can't work with.

So, I'd recommend using GitHub Pages to host your documentation. Check out our workflow
in `.github/workflows/ci.yaml`_ to see how you could set this up. Sorry for that 😕

.. _.github/workflows/ci.yaml: https://github.com/taminomara/sphinx-vhs/blob/main/.github/workflows/ci.yaml
