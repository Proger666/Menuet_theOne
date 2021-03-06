import unittest
from unittest import TestCase
from gluon.dal import DAL, Field

db = DAL('mysql://scorpa:Zaqwerty123@127.0.0.1:1234/menu_db')


from applications.menuet.controllers.bot import weighted_search


class TestWeighted_search(TestCase):
    def setUp(self):
        self.env = new_env(app='menuet', controller='bot')
        self.db = copy_db(self.env, db_name='db', db_link='sqlite:memory')

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
