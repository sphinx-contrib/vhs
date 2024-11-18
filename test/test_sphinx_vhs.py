import pathlib
import xml.etree.ElementTree

import pytest
from html5lib import HTMLParser
from sphinx.testing import util


def parse(fname: pathlib.Path) -> xml.etree.ElementTree.Element:
    with fname.open("rb") as fp:
        return HTMLParser(namespaceHTMLElements=False).parse(fp)


@pytest.fixture()
def patched_generate_vhs_worker_api():
    import sphinx_vhs

    generate_vhs_worker_orig = sphinx_vhs.generate_vhs_worker
    generate_vhs_worker_runs = [0]
    generate_vhs_compilation_runs = [0]

    def generate_vhs_worker(arg):
        runner, chunk, on_tape_done = arg
        generate_vhs_worker_runs[0] += 1
        generate_vhs_compilation_runs[0] += len(chunk)
        generate_vhs_worker_orig(arg)

    sphinx_vhs.generate_vhs_worker = generate_vhs_worker

    def get_generate_vhs_worker_runs():
        return generate_vhs_worker_runs[0]

    def get_generate_vhs_compilation_runs():
        return generate_vhs_compilation_runs[0]

    def reset():
        generate_vhs_worker_runs[0] = 0
        generate_vhs_compilation_runs[0] = 0

    yield get_generate_vhs_worker_runs, get_generate_vhs_compilation_runs, reset

    sphinx_vhs.generate_vhs_worker = generate_vhs_worker_orig


@pytest.mark.sphinx("html", testroot="basics")
def test_app(app: util.SphinxTestApp, patched_generate_vhs_worker_api):
    (
        get_generate_vhs_worker_runs,
        get_generate_vhs_compilation_runs,
        reset,
    ) = patched_generate_vhs_worker_api

    app.build()

    assert get_generate_vhs_worker_runs() == 1  # 1 batch
    assert get_generate_vhs_compilation_runs() == 3  # 3 unique tapes

    outdir = pathlib.Path(app.outdir)

    assert len(list((outdir / "_images").glob("vhs-*.gif"))) == 5

    etree = parse(outdir / "index.html")

    a_tape_gifs = etree.findall(".//img[@alt='a.tape']")
    assert len(a_tape_gifs) == 3
    a_tape_srcs = {e.attrib["src"] for e in a_tape_gifs}
    assert a_tape_srcs == {"_images/vhs-a.gif", "_images/vhs-inline.gif"}

    b_tape_gifs = etree.findall(".//img[@alt='b.tape']")
    assert len(b_tape_gifs) == 3
    b_tape_srcs = {e.attrib["src"] for e in b_tape_gifs}
    assert b_tape_srcs == {"_images/vhs-b.gif", "_images/vhs-inline1.gif"}

    c_tape_gifs = etree.findall(".//img[@alt='c.tape']")
    assert len(c_tape_gifs) == 1
    c_tape_srcs = {e.attrib["src"] for e in c_tape_gifs}
    assert c_tape_srcs == {"_images/vhs-inline2.gif"}

    reset()
    app.build()
    assert get_generate_vhs_worker_runs() == 1
    assert get_generate_vhs_compilation_runs() == 0  # used cached gifs
