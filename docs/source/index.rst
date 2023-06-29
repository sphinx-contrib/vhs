Sphinx plugin for VHS
=====================

You know VHS_, that thing for rendering GIFs from your console?
Well now there's a directive for calling it from your RST docs!

.. _VHS: https://github.com/charmbracelet/vhs

Quickstart
----------

Install the ``sphinx-vhs`` package:

.. code-block:: sh

    pip3 install sphinx-vhs

And add it to your ``conf.py``:

.. code-block:: python

   extensions = [..., 'sphinx_vhs', ...]

Now put some tapes into your source dir,
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
Sphinx-vhs can process tapes in parallel, but only if you let it.

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


Finally, if you'd rather keep tape contents in your RST files,
there's the **vhs-inline**. It also works like a figure_, but, well,
you won't be able to caption it:

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

But can it run inside ReadTheDocs?
----------------------------------

Like all good tools that require non-trivial setup and environment, it can't.
I've tried adding a workaround where sphinx-vhs downloads VHS binary and all dependencies,
but ReadTheDocs seems to use an older version of Linux core, which VHS can't work with.

So, I'd recommend using GitHub Pages to host your documentation. Check out our workflow
in `.github/workflows/docs.yaml`_ to see how you could set this up. Sorry for that 😕

.. _.github/workflows/docs.yaml: https://github.com/taminomara/sphinx-vhs/blob/main/.github/workflows/docs.yaml


.. vhs-inline::
   :scale: 25%

   Type "pwd # 1"
   Enter
   Sleep 5s

.. vhs-inline::
   :scale: 25%

   Type "pwd # 2"
   Enter
   Sleep 5s

.. vhs-inline::
   :scale: 25%

   Type "pwd # 3"
   Enter
   Sleep 5s

.. vhs-inline::
   :scale: 25%

   Type "pwd # 4"
   Enter
   Sleep 5s

.. vhs-inline::
   :scale: 25%

   Type "pwd # 5
   Enter
   Sleep 5s
