from kitefly import Step, Command, Target


def test_tags():
    class HighMem(Command):
        tags = ["highmem"]

    class HighCpu(HighMem):
        tags = ["highcpu"]

    c = HighCpu("some step", "step.sh", tags=["step"])
    assert c.get_tags() == ["highcpu", "highmem", "step"]


def test_targets():
    class PyTest(Command):
        targets = [Target("**/*.py")]
        agents = {"pyenv": "software"}

    c = PyTest("Run Python Tests", "pytest .", targets=[Target("**/test-data.json")])
    patterns = []
    for t in c.get_targets():
        for p in t.patterns:
            patterns.append(str(p))
    assert patterns == ["r/.*[^/]*\\.py/", "r/.*test\\-data\\.json/"]


def test_attrs():
    c = Command(
        "Run command",
        "command.sh",
        priority=10,
        when="pr.branch == 'develop'",
        allow_dependency_failure=True,
        branches="my-branches",
        other="foobar",
    )
    assert "Run command" in str(c)
    assert c.asdict() == {
        "allow_dependency_failure": True,
        "branches": "my-branches",
        "command": "command.sh",
        "if": "pr.branch == 'develop'",
        "key": "run_command",
        "label": "Run command",
        "other": "foobar",
        "priority": 10,
    }


def test_equality():
    c1 = Command("Run command", "command.sh", priority=5)
    c2 = Command("Run command", "command.sh", priority=10)
    c3 = Command("Run command", "command.sh", priority=10)
    c3.key = c2.key
    assert c1 != c2
    assert c2 == c2
    assert c3 == c2
    assert c1 != "foobar"


def test_invalid_deps():
    c1 = Command("Run command", "command.sh", priority=5)
    c2 = Command(label="", command="command.sh")
    c3 = Command("Valid dep", "dep.sh")

    assert c2.key is ""

    value_errors = 0
    try:
        c2 << c1
    except ValueError:
        value_errors += 1

    assert value_errors == 1

    try:
        c1 >> c2
    except ValueError:
        value_errors += 1

    assert value_errors == 2

    c1 >> c3
    assert c1.depends_on == ["valid_dep"]
