import collections
import hashlib
import itertools
import os
import pathlib
import re
import typing as _t

import docutils.nodes
import sphinx.application
import sphinx.builders
import sphinx.environment
import sphinx.errors
import sphinx.util.docutils
import sphinx.util.osutil
import sphinx.util.parallel
import sphinx.writers
import vhs
from docutils.parsers.rst.directives.images import Figure
from sphinx.util import logging
from sphinx.util.console import bold  # type: ignore
from sphinx.util.docutils import SphinxDirective

try:
    from sphinx.util.display import status_iterator  # type: ignore
except ImportError:
    from sphinx.util import status_iterator  # type: ignore


try:
    from sphinx_vhs._version import __version__, __version_tuple__
except ImportError:
    raise ImportError(
        "vhs._version not found. if you are developing locally, "
        "run `pip install -e .[test,doc]` to generate it"
    )


class VhsLoggingAdapter(logging.SphinxLoggerAdapter):
    def process(self, msg, kwargs):
        msg, kwargs = super().process(msg, kwargs)
        return f"[vhs] {msg}", kwargs


vhs._logger = logger = VhsLoggingAdapter(logging.getLogger("sphinx-vhs").logger, {})  # type: ignore


def _get_paths(env: sphinx.environment.BuildEnvironment):
    dest_dir = pathlib.Path(env.app.builder.doctreedir, "vhs_tapes_cache")
    dest_dir.mkdir(parents=True, exist_ok=True)

    img_dir = pathlib.Path(env.app.builder.outdir, env.app.builder.imagedir)
    img_dir.mkdir(parents=True, exist_ok=True)

    return dest_dir, img_dir


def _get_used_files(env: sphinx.environment.BuildEnvironment) -> _t.Dict[str, dict]:
    res = collections.defaultdict(list)
    for f in getattr(env, "vhs_used_files", []):
        res[f["filename"]].append(f)
    return dict(res)


class VhsDirective(SphinxDirective, Figure):
    def run(self):
        figwidth = self.options.get("figwidth")
        if figwidth == "image":
            logger.warning(
                "`figwidth=image` option is not supported for directive %s", self.name
            )

        lines = self._get_tape_contents()

        # remove all comments
        tape = "\n".join(
            [
                prefix
                for line in lines
                if (
                    prefix := re.match(r'^((["\'`]).*?\2|[^"\'`#])*', line)
                    .group(0)
                    .rstrip()
                )
            ]
        )

        filename = "vhs-" + hashlib.sha256(tape.encode()).hexdigest()
        dest_dir = pathlib.Path(self.env.app.builder.doctreedir, "vhs_tapes_cache")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_tape = dest_dir / (filename + ".tape")
        dest_file = str(dest_dir / (filename + ".gif"))

        with dest_tape.open("w") as file:
            file.write(tape)

        if not hasattr(self.env, "vhs_used_files"):
            setattr(self.env, "vhs_used_files", [])
        getattr(self.env, "vhs_used_files").append(
            {
                "docname": self.env.docname,
                "lineno": self.lineno,
                "filename": filename,
            }
        )

        self.arguments = [dest_file]

        (figure_node,) = super().run()

        for orig_node in figure_node.findall(docutils.nodes.image):
            orig_node["uri"] = dest_file
            orig_node["candidates"] = {"*": dest_file}
            vhs_node = VhsNode(orig_node=orig_node)
            orig_node.replace_self(vhs_node)

        return [figure_node]

    def _get_tape_contents(self):
        lines = []
        path = pathlib.Path(self.env.srcdir, self.arguments[0])
        path = path.resolve()
        if not path.exists():
            logger.error("Path %s does not exist", path)
            return []
        elif not path.is_file():
            logger.error("Path %s is not a file", path)
            return []
        else:
            try:
                with path.open() as file:
                    lines.extend(file.read().splitlines())
                    self.state.document.settings.record_dependencies.add(str(path))
            except Exception as e:
                raise self.error(str(e))
        return lines


class InlineVhsDirective(VhsDirective):
    required_arguments = 0
    optional_arguments = 0

    def _get_tape_contents(self):
        self.assert_has_content()
        lines = self.content
        self.content = []  # type: ignore
        return lines


class VhsNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class ProgressReporter(vhs.DefaultProgressReporter):
    _prev_desc = None
    _prev_len = 0

    def __init__(self, verbosity: int):
        super().__init__()

        self._verbosity = verbosity

    def progress(self, desc: str, dl_size: int, total_size: int, speed: float, /):
        if self._verbosity:
            if desc != self._prev_desc:
                logger.info("%s", desc)
        else:
            super().progress(desc, dl_size, total_size, speed)

        self._prev_desc = desc

    def format_desc(self, desc: str) -> str:
        return bold(desc + "...")

    def format_progress(self, dl_size: int, total_size: int, speed: float) -> str:
        dl_size_mb = dl_size / 1024**2
        total_size_mb = total_size / 1024**2
        speed_mb = speed / 1024**2
        progress = dl_size / total_size

        return f" [{progress: >3.0%}] {dl_size_mb:.1f}/{total_size_mb:.1f}MB ({speed_mb:.1f}MB/s)"

    def write(self, msg: str):
        logger.info(msg, nonl=True)


# This runs on `env-before-read-docs` to purge all cached gifs and tapes
# if fresh env (-E) was used. This also runs on `env-updated` to purge
# cached gifs that were used in the previous build, but aren't used now.
def clear_unused_files(
    app: sphinx.application.Sphinx,
    env: sphinx.environment.BuildEnvironment,
    docnames: _t.List[str],
):
    dest_dir, img_dir = _get_paths(env)
    used_files = _get_used_files(env)

    logger.debug("cleaning up old VHS files...")
    for file in itertools.chain(
        dest_dir.glob("vhs-*.gif"),
        dest_dir.glob("vhs-*.tape"),
        img_dir.glob("vhs-*.gif"),
    ):
        name = file.name[: -len(file.suffix)]
        if name not in used_files:
            logger.debug("removing %s", file)
            os.remove(file)


# Merge `vhs_used_files` from one environment into another.
def merge_used_files(
    app: sphinx.application.Sphinx,
    env: sphinx.environment.BuildEnvironment,
    docnames: _t.List[str],
    other: sphinx.environment.BuildEnvironment,
):
    if not hasattr(env, "vhs_used_files"):
        setattr(env, "vhs_used_files", [])
    getattr(env, "vhs_used_files").extend(getattr(other, "vhs_used_files", []))


# Drop `vhs_used_files` entries from an env. This runs when sphinx is going
# to re-read a source file.
def purge_used_files(
    app: sphinx.application.Sphinx,
    env: sphinx.environment.BuildEnvironment,
    docname: str,
):
    if hasattr(env, "vhs_used_files"):
        vhs_used_files = [
            used_files
            for used_files in getattr(env, "vhs_used_files")
            if used_files["docname"] != docname
        ]
        setattr(env, "vhs_used_files", vhs_used_files)


# Actually runs VHS
def generate_vhs(
    app: sphinx.application.Sphinx, env: sphinx.environment.BuildEnvironment
):
    # Another clean-up run after re-reading docs and updating a list of used gifs.
    clear_unused_files(app, env, [])

    dest_dir, img_dir = _get_paths(env)
    used_files = _get_used_files(env)

    paths_to_generate = [
        (
            dest_dir / (file + ".tape"),
            dest_dir / (file + ".gif"),
            env.doc2path(data[0]["docname"]),
            data[0]["lineno"],
        )
        for file, data in used_files.items()
        if not (dest_dir / (file + ".gif")).exists()
    ]

    if not paths_to_generate:
        logger.debug("no outdated tapes")
        return

    try:
        runner = vhs.resolve(
            min_version=app.config["vhs_min_version"],
            cwd=app.config["vhs_cwd"] or env.srcdir,
            reporter=ProgressReporter(app.verbosity),
            install=app.config["vhs_auto_install"],
            cache_path=app.config["vhs_auto_install_location"],
        )
    except vhs.VhsError as e:
        raise sphinx.errors.ExtensionError(str(e)) from e

    tasks: _t.Union[
        sphinx.util.parallel.ParallelTasks, sphinx.util.parallel.SerialTasks
    ]
    if sphinx.util.parallel.parallel_available and app.parallel > 1:
        tasks = sphinx.util.parallel.ParallelTasks(app.parallel)
    else:
        tasks = sphinx.util.parallel.SerialTasks()

    if app.parallel > 1:
        chunks = sphinx.util.parallel.make_chunks(paths_to_generate, app.parallel)  # type: ignore
    else:
        chunks = [paths_to_generate]

    logger.debug(
        "rendering VHS tapes: %s files, parallel=%s",
        len(paths_to_generate),
        app.parallel,
    )

    progress = status_iterator(
        range(len(chunks)),
        "rendering VHS tapes... ",
        "teal",
        len(chunks),
        app.verbosity,
    )

    next(progress)

    def on_chunk_done(*args, **kwargs):
        try:
            next(progress)
        except StopIteration:
            pass

    for chunk in chunks:
        tasks.add_task(generate_vhs_worker, (runner, chunk), on_chunk_done)

    tasks.join()


def generate_vhs_worker(arg):
    runner, chunk = arg
    for src_file, dst_file, docname, lineno in chunk:
        logger.debug("rendering %s", src_file)
        try:
            runner.run(src_file, dst_file)
        except vhs.VhsError as e:
            raise sphinx.errors.ExtensionError(f"at {docname}:{lineno}:\n{e}") from e


def process_vhs_nodes(
    app: sphinx.application.Sphinx, doctree: docutils.nodes.Node, fromdocname: str
):
    env = app.builder.env

    for vhs_node in doctree.findall(VhsNode):
        orig_node = vhs_node["orig_node"]
        env.images.add_file(fromdocname, orig_node["uri"])
        vhs_node.replace_self(orig_node)


def setup(app: sphinx.application.Sphinx):
    app.add_config_value("vhs_min_version", "0.5.0", rebuild=False)
    app.add_config_value("vhs_auto_install_location", None, rebuild=False)
    app.add_config_value("vhs_auto_install", True, rebuild=False)
    app.add_config_value("vhs_cwd", None, rebuild=True)

    app.add_directive("vhs", VhsDirective)
    app.add_directive("vhs-inline", InlineVhsDirective)

    app.connect("env-before-read-docs", clear_unused_files)
    app.connect("env-merge-info", merge_used_files)
    app.connect("env-purge-doc", purge_used_files)
    app.connect("env-updated", generate_vhs)
    app.connect("doctree-resolved", process_vhs_nodes)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
