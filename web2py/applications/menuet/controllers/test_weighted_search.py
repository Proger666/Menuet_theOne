import unittest
from unittest import TestCase



from applications.menuet.controllers.bot import weighted_search


class TestWeighted_search(TestCase):

    def test_weighted_search(self):
        query = "meTest"
        result = weighted_search(query, 33, 55, 1, "cheap")
        self.failUnless(result == "a")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestWeighted_search())
    return suite


if __name__ == '__main__':
    runner = unittest.test_weighted_search()
    test_suite = suite()
    runner.run()
