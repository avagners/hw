import random
import unittest

from Stack import Stack


class TestStack(unittest.TestCase):

    def setUp(self):
        self.s_stack = Stack()

    # постусловие: в стек добавлено новое значение
    def test_push(self):
        len_stack = len(self.s_stack.stack)
        self.assertEqual(len_stack, 0)


if __name__ == '__main__':
    unittest.main()
