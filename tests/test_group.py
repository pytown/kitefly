from kitefly import Group, Command


def test_group_combinations():
    pre = Command("Pre-command", "pre-command.sh")
    c1 = Command("Group combo test", "test.sh")
    c2 = Command("Group combo test #2", "test2.sh")
    c3 = Command("Group combo test #3", "test3.sh")
    c4 = Command("Group combo test #4", "test4.sh")

    g1 = Group(c1, c2, Group(c3)) + Group(c4)
    g1 >> pre
    assert len(g1.steps()) == 4
    for c in (c1, c2, c3, c4):
        assert c.depends_on == ["pre_command"]
