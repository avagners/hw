import random
import unittest

from Deque import Deque


class TestDeque(unittest.TestCase):

    def setUp(self):
        self.s_deque = Deque()

    def test_add_front(self):
        len_queue = len(self.s_deque.deque)
        item1 = random.randint(0, 100)
        self.s_deque.addFront(item1)
        self.assertEqual(len(self.s_deque.deque), len_queue + 1)
        self.assertEqual(self.s_deque.deque[0], item1)
        item2 = random.randint(0, 100)
        self.s_deque.addFront(item2)
        self.assertEqual(len(self.s_deque.deque), len_queue + 2)
        self.assertEqual(self.s_deque.deque[0], item2)

    def test_empty_add_tail(self):
        len_queue = len(self.s_deque.deque)
        item1 = random.randint(0, 100)
        self.s_deque.addTail(item1)
        self.assertEqual(len(self.s_deque.deque), len_queue + 1)
        self.assertEqual(self.s_deque.deque[-1], item1)
        item2 = random.randint(0, 100)
        self.s_deque.addTail(item2)
        self.assertEqual(len(self.s_deque.deque), len_queue + 2)
        self.assertEqual(self.s_deque.deque[-1], item2)


if __name__ == '__main__':
    unittest.main()
