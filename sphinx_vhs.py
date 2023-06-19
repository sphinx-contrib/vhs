import hashlib
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request

from docutils.parsers.rst.directives.images import Figure
import docutils.nodes
import sphinx.application
import sphinx.writers
try:
    from sphinx.util.display import status_iterator
except ImportError:
    from sphinx.util import status_iterator
import sphinx.util.parallel
import sphinx.util.osutil
import sphinx.util.docutils
import sphinx.builders
from sphinx.util.console import bold
from sphinx.util.docutils import SphinxDirective
from sphinx.util import logging


logger = logging.getLogger('sphinx-vhs')

# If we're running on readthedocs, we'll download vhs for user.
vhs_url = 'https://github.com/charmbracelet/vhs/releases/download/v0.5.0/vhs_0.5.0_Linux_x86_64.tar.gz'
ttyd_url = 'https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64'
ffmpeg_url = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'


class VhsDirective(SphinxDirective, Figure):
    def run(self):
        figwidth = self.options.get('figwidth')
        if figwidth == 'image':
            logger.warn('`figwidth=image` option is not supported for directive %s', self.name)

        lines = self._get_tape_contents()

        # remove all comments
        tape = '\n'.join([
            prefix for line in lines if (prefix := re.match(r'^((["\'`]).*?\2|[^"\'`#])*', line).group(0).rstrip())
        ])

        filename = 'vhs-' + hashlib.sha256(tape.encode()).hexdigest()
        dest_dir = pathlib.Path(self.env.app.builder.doctreedir, 'vhs_tapes_cache')
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_tape = dest_dir / (filename + '.tape')
        dest_file = str(dest_dir / (filename + '.gif'))

        with dest_tape.open('w') as file:
            file.write(tape)

        if not hasattr(self.env, 'vhs_used_files'):
            setattr(self.env, 'vhs_used_files', [])
        getattr(self.env, 'vhs_used_files').append({
            'docname': self.env.docname,
            'lineno': self.lineno,
            'filename': filename,
        })

        self.arguments = [dest_file]

        figure_node, = super().run()

        for orig_node in figure_node.findall(docutils.nodes.image):
            orig_node['uri'] = dest_file
            orig_node['candidates'] = {'*': dest_file}
            vhs_node = VhsNode(orig_node=orig_node)
            orig_node.replace_self(vhs_node)

        return [figure_node]

    def _get_tape_contents(self):
        lines = []
        path = pathlib.Path(self.env.srcdir, self.arguments[0])
        path = path.resolve()
        if not path.exists():
            logger.error('Path %s does not exist', path)
            return []
        elif not path.is_file():
            logger.error('Path %s is not a file', path)
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
        self.content = []
        return lines


class VhsNode(docutils.nodes.General, docutils.nodes.Element):
    pass


def merge_used_files(app, env, docnames, other):
    if not hasattr(env, 'vhs_used_files'):
        env.vhs_used_files = []
    env.vhs_used_files.extend(getattr(other, 'vhs_used_files', []))


def purge_used_files(app, env, docname):
    if hasattr(env, 'vhs_used_files'):
        env.vhs_used_files = [used_files for used_files in env.vhs_used_files if used_files['docname'] != docname]


def generate_vhs(app, env):
    dest_dir = pathlib.Path(env.app.builder.doctreedir, 'vhs_tapes_cache')
    dest_dir.mkdir(parents=True, exist_ok=True)

    img_dir = pathlib.Path(env.app.builder.outdir, env.app.builder.imagedir)
    img_dir.mkdir(parents=True, exist_ok=True)

    used_files = {f['filename'] for f in getattr(env, 'vhs_used_files', [])}

    logger.debug('[vhs] cleaning up old VHS files...')
    for file in dest_dir.glob('vhs-*.gif'):
        if not file.name[:-len('.gif')] in used_files:
            os.remove(file)
            logger.debug('[vhs] removed %s', file)
    for file in img_dir.glob('vhs-*.gif'):
        if not file.name[:-len('.gif')] in used_files:
            os.remove(file)
            logger.debug('[vhs] removed %s', file)
    for file in dest_dir.glob('vhs-*.tape'):
        if not file.name[:-len('.tape')] in used_files:
            os.remove(file)
            logger.debug('[vhs] removed %s', file)

    paths_to_generate = [
        (dest_dir / (file + '.tape'), dest_dir / (file + '.gif')) for file in used_files
    ]
    paths_to_generate = [
        (src_file, dst_file) for src_file, dst_file in paths_to_generate if not dst_file.exists()
    ]

    if not paths_to_generate:
        return

    if not shutil.which('vhs'):
        if sys.platform == 'darwin':
            logger.error('VHS is not installed on your system.\n'
                         'Run "brew install vhs", or find additional installation instructions\n'
                         'at https://github.com/charmbracelet/vhs#installation')
        else:
            logger.error('VHS is not installed on your system.\n'
                         'Find installation instructions at https://github.com/charmbracelet/vhs#installation')
        raise RuntimeError('vhs is not installed on your system')

    if sphinx.util.parallel.parallel_available and app.parallel > 1:
        tasks = sphinx.util.parallel.ParallelTasks(app.parallel)
    else:
        tasks = sphinx.util.parallel.SerialTasks()

    chunks = sphinx.util.parallel.make_chunks(paths_to_generate, app.parallel)

    progress = status_iterator(
        [''] * len(chunks), 'rendering VHS tapes... ', 'teal', len(chunks), app.verbosity
    )

    next(progress)

    def on_chunk_done(*args, **kwargs):
        try:
            next(progress)
        except StopIteration:
            pass

    for chunk in chunks:
        tasks.add_task(generate_single_vhs, (env.srcdir, chunk), on_chunk_done)

    tasks.join()


def generate_single_vhs(arg):
    cwd, chunk = arg
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        tmp_file = tempfile.mktemp(suffix='.gif', dir=tmp_dir)
        for src_file, dst_file in chunk:
            logger.debug('[vhs] rendering VHS file %s into %s', src_file, tmp_file)
            result = subprocess.run(
                ['vhs', src_file, '-q', '-o', tmp_file],
                stdin=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                cwd=cwd,
            )
            if result.returncode:
                raise RuntimeError(
                    f'VHS render failed for tape {src_file}.\n\n'
                    f'Stderr:\n{result.stderr}\n\n'
                    f'Stdout:\n{result.stdout}'
                )
            logger.debug('[vhs] copying VHS file %s to %s', tmp_file, dst_file)
            os.replace(tmp_file, dst_file)
    finally:
        shutil.rmtree(tmp_dir)


def process_vhs_nodes(app, doctree, fromdocname):
    env = app.builder.env

    for vhs_node in doctree.findall(VhsNode):
        orig_node = vhs_node['orig_node']
        env.images.add_file(fromdocname, orig_node['uri'])
        vhs_node.replace_self(orig_node)


def setup(app):
    app.add_directive('vhs', VhsDirective)
    app.add_directive('vhs-inline', InlineVhsDirective)

    app.connect('env-purge-doc', purge_used_files)
    app.connect('env-merge-info', merge_used_files)
    app.connect('env-updated', generate_vhs)
    app.connect('doctree-resolved', process_vhs_nodes)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
