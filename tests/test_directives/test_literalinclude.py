"""Test cases for ``revealjs-literalinclude`` directive."""
import pytest
from sphinx.testing.util import SphinxTestApp
from testutils import soup_html


@pytest.mark.sphinx("revealjs", testroot="default")
def test_inherit_literalinclude(app: SphinxTestApp, status, warning):  # noqa
    soup = soup_html(app, "with-revealjs-literalinclude.html")
    code_tag = soup.find_all("code")[0]
    assert "python" in code_tag.attrs["class"]


@pytest.mark.sphinx("revealjs", testroot="default")
def test_dataline(app: SphinxTestApp, status, warning):  # noqa
    soup = soup_html(app, "with-revealjs-literalinclude.html")
    code_tag = soup.find_all("code")[1]
    assert "python" in code_tag.attrs["class"]
    assert "data-line-numbers" in code_tag.attrs