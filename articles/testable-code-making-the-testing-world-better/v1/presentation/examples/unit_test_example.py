import unittest


def something():
    return [42]


class TestSomething(unittest.TestCase):

    def test_feature(self):
        self.assertEqual(something(), [42])

    def test_failure(self):
        self.assertEqual(something(), [7])


if __name__ == '__main__':
    unittest.main()
