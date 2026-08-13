import unittest

from broken import add_numbers


class AddNumbersTest(unittest.TestCase):
    def test_adds_positive_numbers(self):
        self.assertEqual(add_numbers(2, 3), 5)

    def test_adds_values_that_cancel(self):
        self.assertEqual(add_numbers(-1, 1), 0)
