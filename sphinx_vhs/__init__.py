import base64
import collections
import hashlib
import os
import pathlib
import re
import shutil
import typing as _t
from dataclasses import dataclass
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool

import docutils.nodes
import docutils.statemachine
import sphinx.application
import sphinx.environment
import sphinx.errors
import sphinx.util.parallel
import vhs
from docutils.parsers.rst.directives.images import Figure
from sphinx.transforms import SphinxTransform
from sphinx.util import logging
from sphinx.util.console import colorize, term_width_line
from sphinx.util.docutils import SphinxDirective

from sphinx_vhs._version import *

vhs._logger = _logger = logging.getLogger(  # pyright: ignore[reportPrivateUsage]
    "sphinx-vhs"
)


@dataclass(unsafe_hash=True)
class VhsData:
    docname: str
    lineno: int
    tape_hash: str
    tape_file: pathlib.Path
    render_file: pathlib.Path
    gif_file: pathlib.Path
    origname: str


def _get_used_files(
    env: sphinx.environment.BuildEnvironment,
) -> _t.Dict[str, list[VhsData]]:
    res = collections.defaultdict(list)
    for f in getattr(env, "vhs_used_files", set()):
        res[f.tape_hash].append(f)
    return dict(res)


class VhsDirective(SphinxDirective, Figure):
    def run(self):
        lines = self._get_tape_contents_inlined()
        tape = "\n".join(lines)

        filename = "vhs-" + (self._get_gif_filename() or "inline")
        tape_hash = base64.urlsafe_b64encode(
            hashlib.sha256(tape.encode()).digest()
        ).decode()
        dest_dir = pathlib.Path(
            self.env.app.builder.doctreedir,
            "vhs_tapes_cache",
            tape_hash,
        )
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_tape = dest_dir / ("vhs.tape")
        dest_render = dest_dir / ("vhs.gif")
        dest_file = dest_dir / (filename + ".gif")

        with dest_tape.open("w") as file:
            file.write(tape)

        if not hasattr(self.env, "vhs_used_files"):
            setattr(self.env, "vhs_used_files", set())
        getattr(self.env, "vhs_used_files").add(
            VhsData(
                docname=self.env.docname,
                lineno=self.lineno,
                tape_hash=tape_hash,
                tape_file=dest_tape,
                render_file=dest_render,
                gif_file=dest_file,
                origname=(
                    self.env.relfn2path(self.arguments[0])[0]
                    if self.arguments
                    else "<inline>"
                ),
            )
        )

        # We have to use data uri to obscure the fact that the image
        # is generated later. If we were to use `dest_file` directly,
        # HTML builder would complain that image doesn't exist.
        # We substitute actual URI in `ProcessVhsNodes`.
        self.arguments = [f"data:vhs-tape;{dest_file}"]
        return super().run()

    def _get_gif_filename(self) -> str | None:
        name = pathlib.Path(self.arguments[0]).name
        if name.endswith(".tape"):
            return name[:-5]
        elif name.endswith(".vhs"):
            return name[:-4]
        else:
            return name

    def _get_tape_contents(
        self, path: _t.Optional[pathlib.Path] = None
    ) -> tuple[list[str], pathlib.Path | str]:
        if path is None:
            relpath, abspath = self.env.relfn2path(self.arguments[0])
            path = pathlib.Path(abspath)
        else:
            path = path.expanduser().resolve()
            relpath = path.relative_to(self.env.srcdir, walk_up=True)
        self.env.note_dependency(path)
        if not path.exists():
            _logger.error("Path %s does not exist", path, type="vhs")
            return [], relpath
        elif not path.is_file():
            _logger.error("Path %s is not a file", path, type="vhs")
            return [], relpath
        else:
            try:
                with path.open() as file:
                    lines = file.read().splitlines()
                    self.state.document.settings.record_dependencies.add(str(path))
            except Exception as e:
                raise self.error(str(e))

        return lines, relpath

    def _get_tape_contents_inlined(self):
        seen: list[pathlib.Path] = []
        imports: list[tuple[str, str, int]] = []

        cwd = pathlib.Path(self.env.app.config["vhs_cwd"] or self.env.srcdir)

        def inline(lines: list[str], path: pathlib.Path | str):
            flatten_lines = []
            for i, line in enumerate(lines):
                if match := re.match(
                    r"^\s*Source\s+['\"`]?(?P<path>.*?)['\"`]?\s*$", line, re.IGNORECASE
                ):
                    next_path = (cwd / match.group("path")).expanduser().resolve()
                    if next_path in seen:
                        include_chain = "\n  -> ".join(
                            f"{orig}:{ln + 1}: {what}" for (orig, what, ln) in imports
                        )
                        raise self.error(
                            f"Circular include detected in this tape:\n  -> {include_chain}\n"
                        )
                    seen.append(next_path)
                    imports.append((str(path), match.group(), i))
                    self.env.note_dependency(path)
                    flatten_lines.extend(inline(*self._get_tape_contents(next_path)))
                    seen.pop()
                    imports.pop()
                elif match := re.match(r'^((["\'`]).*?\2|[^"\'`#])*', line):
                    line = match.group().strip()
                    if line:
                        flatten_lines.append(match.group().strip())

            return flatten_lines

        return inline(*self._get_tape_contents())


class InlineVhsDirective(VhsDirective):
    required_arguments = 0
    optional_arguments = 0

    def _get_gif_filename(self) -> str | None:
        return None

    def _get_tape_contents(
        self, path: _t.Optional[pathlib.Path] = None
    ) -> tuple[list[str], pathlib.Path | str]:
        if path:
            return super()._get_tape_contents(path)

        self.assert_has_content()
        lines: list[str] = list(self.content)
        self.content = docutils.statemachine.StringList()
        return lines, "<inline>"


class ProgressReporter(vhs.DefaultProgressReporter):
    _prev_desc = None
    _prev_len = 0

    def __init__(self, verbosity: int):
        super().__init__()

        self._verbosity = verbosity

    def progress(self, desc: str, dl_size: int, total_size: int, speed: float, /):
        if self._verbosity:
            if desc != self._prev_desc:
                _logger.info("%s", desc, type="vhs")
        else:
            super().progress(desc, dl_size, total_size, speed)

        self._prev_desc = desc

    def format_desc(self, desc: str) -> str:
        return colorize("bold", desc + "...")

    def format_progress(self, dl_size: int, total_size: int, speed: float) -> str:
        dl_size_mb = dl_size / 1024**2
        total_size_mb = total_size / 1024**2
        speed_mb = speed / 1024**2
        progress = dl_size / total_size

        return f" [{progress: >3.0%}] {dl_size_mb:.1f}/{total_size_mb:.1f}MB ({speed_mb:.1f}MB/s)"

    def write(self, msg: str):
        _logger.info(msg, nonl=True, type="vhs")


def clear_unused_files(
    env: sphinx.environment.BuildEnvironment,
):
    dest_dir = pathlib.Path(env.app.builder.doctreedir, "vhs_tapes_cache")
    dest_dir.mkdir(parents=True, exist_ok=True)
    used_files = _get_used_files(env)

    _logger.debug("cleaning up old VHS files...", type="vhs")
    for dir in dest_dir.glob("*"):
        if dir.name not in used_files:
            modified = datetime.fromtimestamp(dir.stat().st_mtime)
            if datetime.now() - modified > env.config["vhs_cleanup_delay"]:
                _logger.debug("removing %s", dir, type="vhs")
                shutil.rmtree(dir)


# Merge `vhs_used_files` from one environment into another.
def merge_used_files(
    app: sphinx.application.Sphinx,
    env: sphinx.environment.BuildEnvironment,
    docnames: _t.List[str],
    other: sphinx.environment.BuildEnvironment,
):
    if not hasattr(env, "vhs_used_files"):
        setattr(env, "vhs_used_files", set())
    getattr(env, "vhs_used_files").update(getattr(other, "vhs_used_files", set()))


# Drop `vhs_used_files` entries from an env. This runs when sphinx is going
# to re-read a source file.
def purge_used_files(
    app: sphinx.application.Sphinx,
    env: sphinx.environment.BuildEnvironment,
    docname: str,
):
    if hasattr(env, "vhs_used_files"):
        vhs_used_files = {
            used_files
            for used_files in getattr(env, "vhs_used_files")
            if used_files.docname != docname
        }
        setattr(env, "vhs_used_files", vhs_used_files)


# Actually runs VHS
def generate_vhs(
    app: sphinx.application.Sphinx, env: sphinx.environment.BuildEnvironment
):
    # Another clean-up run after re-reading docs and updating a list of used gifs.
    clear_unused_files(env)

    used_files = _get_used_files(env)

    outdated_files = [
        data[0] for data in used_files.values() if not data[0].render_file.exists()
    ]

    if outdated_files:
        environ = os.environ.copy()
        if "READTHEDOCS" in environ:
            environ["VHS_NO_SANDBOX"] = "true"
        try:
            runner = vhs.resolve(
                min_version=app.config["vhs_min_version"],
                max_version=app.config["vhs_max_version"],
                cwd=app.config["vhs_cwd"] or env.srcdir,
                reporter=ProgressReporter(app.verbosity),
                install=app.config["vhs_auto_install"],
                cache_path=app.config["vhs_auto_install_location"],
                env=environ,
            )
        except vhs.VhsError as e:
            raise sphinx.errors.ExtensionError(str(e)) from e

        in_progress = collections.Counter(p.origname for p in outdated_files)

        def on_tape_done(origname: str | None):
            if app.verbosity:
                return

            if origname:
                orignames_left = in_progress[origname] - 1
                if orignames_left > 0:
                    in_progress[origname] = orignames_left
                else:
                    in_progress.pop(origname, None)

            total = len(outdated_files)
            left = in_progress.total()
            done = total - left
            tape = f" {sorted(in_progress)[0]}" if in_progress else ""
            if left > 1:
                tape += f" +{left - 1} more"
            _logger.info(
                term_width_line(
                    f"{colorize("bold", "rendering VHS tapes...")} [{done}/{total}]{colorize("teal", tape)}"
                ),
                nonl=True,
            )

        if (
            len(outdated_files) > 1
            and sphinx.util.parallel.parallel_available
            and app.parallel <= 1
        ):
            _logger.info(
                colorize(
                    "yellow",
                    "rendering VHS tapes in sequence; pass -j auto to enable parallel run",
                ),
                type="vhs",
            )
        if app.verbosity:
            _logger.info(
                f"{colorize("bold", "rendering VHS tapes")}: %s files, parallel=%s",
                len(outdated_files),
                app.parallel,
                type="vhs",
            )
        else:
            on_tape_done(None)

        def worker(arg: VhsData):
            _logger.debug("rendering %s", arg.tape_file, type="vhs")
            try:
                runner.run(arg.tape_file, arg.render_file)
            except vhs.VhsError as e:
                path = env.doc2path(arg.docname)
                raise sphinx.errors.ExtensionError(
                    f"at {path}:{arg.lineno}:\n{e}"
                ) from e
            on_tape_done(arg.origname)

        with ThreadPool(app.parallel or 1) as tasks:
            for _ in tasks.imap_unordered(worker, outdated_files):
                pass

        if not app.verbosity:
            _logger.info("")

    for instances in used_files.values():
        for data in instances:
            if data.render_file != data.gif_file and not data.gif_file.exists(
                follow_symlinks=False
            ):
                _logger.debug("make link: %s -> %s", data.render_file, data.gif_file)
                try:
                    data.gif_file.symlink_to(data.render_file)
                except NotImplementedError:
                    shutil.copyfile(data.render_file, data.gif_file)
            else:
                _logger.debug(
                    "already linked: %s -> %s", data.render_file, data.gif_file
                )


class ProcessVhsNodes(SphinxTransform):
    # We need to run before image converters, data extractors, etc.
    default_priority = 100

    def apply(self, **kwargs: _t.Any):
        for image in self.document.findall(docutils.nodes.image):
            uri = image["uri"]
            if uri.startswith("data:vhs-tape;"):
                uri = uri[len("data:vhs-tape;") :]
                image["uri"] = uri
                image["candidates"] = {"*": uri, "image/gif": uri}
                self.env.images.add_file(self.env.docname, image["uri"])


def setup(app: sphinx.application.Sphinx):
    app.add_config_value("vhs_min_version", "0.5.0", rebuild="env")
    app.add_config_value("vhs_max_version", "2.0.0", rebuild="env")
    app.add_config_value("vhs_auto_install_location", None, rebuild="")
    app.add_config_value("vhs_auto_install", True, rebuild="")
    app.add_config_value("vhs_cwd", None, rebuild="env")
    app.add_config_value(
        "vhs_cleanup_delay", timedelta(days=1), rebuild="env", types=timedelta
    )

    app.add_directive("vhs", VhsDirective)
    app.add_directive("vhs-inline", InlineVhsDirective)

    app.connect("env-merge-info", merge_used_files)
    app.connect("env-purge-doc", purge_used_files)
    app.connect("env-updated", generate_vhs)
    app.add_post_transform(ProcessVhsNodes)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
