from kitefly.util import generate_key, as_iterable


def test_generate_key():
    assert generate_key("Some Label") == "some_label"
    assert generate_key("Some   Label") == "some_label__kf__1"


def test_as_iterable():
    assert as_iterable([1]) == [1]
    assert as_iterable(True) == (True,)
