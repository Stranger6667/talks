

def something():
    return [42]


def test_feature():
    assert something() == [42]


def test_failure():
    assert something() == [7]
