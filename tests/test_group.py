from kitefly import Group, Command


def test_group_combinations():
    pre = Command("Pre-command", "pre-command.sh")
    c1 = Command("Group combo test", "test.sh")
    c2 = Command("Group combo test #2", "test2.sh")
    c3 = Command("Group combo test #3", "test3.sh")
    c4 = Command("Group combo test #4", "test4.sh")

    g1 = Group([c1, c2])
    assert len(g1.steps) == 2
    g2 = Group([c3, c4])
    assert len(g2.steps) == 2
    g1 += g2
    assert len(g1.steps) == 4
    g1 >> pre
    assert len(g1.steps) == 4
    for c in (c1, c2, c3, c4):
        assert c.depends_on == ["pre_command"]


def test_nested_groups_flattened():
    c1 = Command("Group combo test", "test.sh", key="c1")
    c2 = Command("Group combo test #2", "test2.sh", key="c2")
    g1 = Group([c1, Group([c2], key="group2")])
    assert [s.key for s in g1.steps] == ["c1", "c2"]

def test_group_addition():
    c1 = Command("Group combo test", "test.sh", key="c1")
    c2 = Command("Group combo test #2", "test2.sh", key="c2")
    c3 = Command("Group combo test #3", "test3.sh", key="c3")
    g1 = Group([c1])
    g2 = Group([c2])
    g3 = g1 + g2
    g4 = g3 + c3
    assert [s.key for s in g4.steps] == ["c1", "c2", "c3"]
