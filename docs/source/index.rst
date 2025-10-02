Sphinx plugin for VHS
=====================

Sphinx-VHS is an integration plugin for Sphinx and VHS_,
a tool by charm_ that renders terminal commands into GIFs.
It allows referencing ``.tape`` files form your docs,
and rendering them during sphinx build.

.. _VHS: https://github.com/charmbracelet/vhs

.. _charm: https://charm.sh/


.. toctree::
    :hidden:
    :caption: Links

    GitHub <https://github.com/sphinx-contrib/vhs/>


Quickstart
----------

1. Install the ``sphinx-vhs`` package:

   .. code-block:: console

       $ pip install sphinx-vhs

2. And add it to your ``conf.py``:

   .. code-block:: python

      extensions = ["sphinx_vhs", ...]

3. Now put some tapes into your documentation source dir,
   and use the **vhs** directive to render them:

   .. code-block:: rst

      .. vhs:: /_tapes/simple.tape
         :alt: A gif showing some hello-world text being typed into console.

   .. dropdown:: Example output

      .. highlights::

         .. vhs:: /_tapes/simple.tape
            :alt: A gif showing some hello-world text being typed into console.

Oh, and don't forget to compile with ``SPHINXOPTS="-j auto"`` to speed things up.
Sphinx-VHS can process tapes in parallel, but only if you let it.


Usage
-----

.. rst:directive:: .. vhs:: <path>

   The **vhs** directive has all the same attributes as the figure_,
   so you can caption it and reference it. Path is relative to the current doc file;
   if it starts with ``/``, it is relative to the content root, just like with
   the figure_ directive.

   **Example:**

   .. code-block:: rst

      .. vhs:: /_tapes/simple.tape
         :alt: A gif showing some hello-world text being typed into console.
         :name: gif-reference

         Look, a small :ref:`gif <gif-reference>`! Isn't it cute?

   .. dropdown:: Example output

      .. vhs:: /_tapes/simple.tape
         :alt: A gif showing some hello-world text being typed into console.
         :name: gif-reference

         Look, a :ref:`gif <gif-reference>`! Isn't it cute?

.. rst:directive:: .. vhs-inline::

   There's also **vhs-inline**, which lets you paste a small tape right
   into your documentation. It also works like a figure_,
   but, well, you won't be able to caption it:

   .. code-block:: rst

      .. vhs-inline::

         Type "pwd"
         Sleep 500ms
         Enter
         Sleep 500ms
         Type "ls -l"
         Sleep 500ms
         Enter
         Sleep 5s

   .. dropdown:: Example output

      .. vhs-inline::

         Type "pwd"
         Sleep 500ms
         Enter
         Sleep 500ms
         Type "ls -l"
         Sleep 500ms
         Enter
         Sleep 3s

.. _figure: https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure


Settings
--------

Sphinx-VHS adds the following settings to ``conf.py``:

.. py:data:: vhs_min_version
   :type: bool

   Minimum VHS version required to render types.

   Default: ``"0.5.0"``.

.. py:data:: vhs_max_version
   :type: bool

   Maximum VHS version required to render types. Set to `None` to disable maximum
   version checking.

   Default: ``"2.0.0"``.

.. py:data:: vhs_cwd
   :type: bool

   Working dir for VHS runs. Affects ``Source`` commands in tapes.

   Default: documentation source dir.

.. py:data:: vhs_auto_install
   :type: bool

   Whether to install VHS in case it is missing or outdated.

   Default: `True`.

.. py:data:: vhs_auto_install_location
   :type: pathlib.Path | str

   Path where VHS binaries should be installed to.

   Default: see :func:`vhs.default_cache_path`.

.. py:data:: vhs_cleanup_delay
   :type: datetime.timedelta

   Sphinx VHS will delete unused GIFs after this period.

   Default: 1 day.


FAQ
---

**Build fails with `No usable sandbox! Update your kernel...`**

If you're running your build in CI that doesn't enable sandbox API within
its containers, you can set environment variable `VHS_NO_SANDBOX=true`.
