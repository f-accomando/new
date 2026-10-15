"""End-to-end smoke test (illustration: shows the shape ci_audit.py looks for)."""


def expect(text, timeout=10):
    return text, timeout


def test_index_rebuild():
    expect("index rebuild finished", timeout=30)


def test_search_ready():
    expect("search ready", timeout=5)
