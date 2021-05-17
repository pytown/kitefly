from kitefly.util import generate_key

def test_generate_key():
    assert generate_key("Some Label") == "some_label"
    assert generate_key("Some   Label") == "some_label__kf__1"
