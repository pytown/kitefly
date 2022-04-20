import re
import pytest

from kitefly import Target


def test_target_matching():
    t = Target("**/*.md")
    assert t.matches("foo/bar/doc.md")
    assert t.matches("README.md")
    assert not t.matches("foo/bar/file.py")


def test_target_comparison():
    t_md = Target("**/*.md")
    t_src = Target("application/source_files/**/*.py")
    t_md_highprio = Target("**/*.md", 10)
    assert t_src > t_md
    assert t_md_highprio > t_src
    assert t_md_highprio > t_md
    assert t_md < t_md_highprio
    assert t_md < t_src


def test_target_regex():
    t_md = Target(re.compile(r".*\.md"))
    assert t_md.matches("foo/bar/doc.md")
    assert not t_md.matches("foo/bar/file.py")


def test_target_pattern_debug():
    t_md = Target("**/*.md")
    assert str(t_md.patterns[0]) == "r/.*[^/]*\\.md/"
    assert "Target(" in str(t_md)


def test_dependencies():
    t_md = Target("**/*.md")
    t_doc = Target("docs/**")
    t_doc >> t_md
    assert len(t_doc.dependencies) == 1
    assert len(t_md.dependencies) == 0
    assert t_md.matches("README.md")
    assert t_doc.matches("README.md")
