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

    def generate_vhs_worker(*args, **kwargs):
        generate_vhs_worker_runs[0] += 1
        generate_vhs_worker_orig(*args, **kwargs)

    sphinx_vhs.generate_vhs_worker = generate_vhs_worker

    def get_generate_vhs_worker_runs():
        return generate_vhs_worker_runs[0]

    def reset_generate_vhs_worker_runs():
        generate_vhs_worker_runs[0] = 0

    yield get_generate_vhs_worker_runs, reset_generate_vhs_worker_runs

    sphinx_vhs.generate_vhs_worker = generate_vhs_worker_orig


@pytest.mark.sphinx("html", testroot="basics")
def test_app(app: util.SphinxTestApp, patched_generate_vhs_worker_api):
    (
        get_generate_vhs_worker_runs,
        reset_generate_vhs_worker_runs,
    ) = patched_generate_vhs_worker_api

    app.build()

    assert get_generate_vhs_worker_runs() == 1  # 1 batch

    outdir = pathlib.Path(app.outdir)

    assert len(list((outdir / "_images").glob("vhs-*.gif"))) == 3

    etree = parse(outdir / "index.html")

    a_tape_gifs = etree.findall(".//img[@alt='a.tape']")
    assert len(a_tape_gifs) == 3
    a_tape_srcs = {e.attrib["src"] for e in a_tape_gifs}
    assert len(a_tape_srcs) == 1

    b_tape_gifs = etree.findall(".//img[@alt='b.tape']")
    assert len(b_tape_gifs) == 3
    b_tape_srcs = {e.attrib["src"] for e in b_tape_gifs}
    assert len(b_tape_srcs) == 1

    c_tape_gifs = etree.findall(".//img[@alt='c.tape']")
    assert len(c_tape_gifs) == 1
    c_tape_srcs = {e.attrib["src"] for e in c_tape_gifs}
    assert len(c_tape_srcs) == 1

    assert len(a_tape_srcs | b_tape_srcs | c_tape_srcs) == 3

    reset_generate_vhs_worker_runs()
    app.build()
    assert get_generate_vhs_worker_runs() == 0  # used cached gifs
