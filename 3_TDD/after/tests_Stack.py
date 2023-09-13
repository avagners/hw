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
        new_item = random.randint(0, 100)
        self.s_stack.push(new_item)
        self.assertEqual(len(self.s_stack.stack), len_stack + 1)
        self.assertEqual(self.s_stack.stack[-1], new_item)
        new_item = random.randint(0, 100)
        self.s_stack.push(new_item)
        self.assertEqual(len(self.s_stack.stack), len_stack + 2)
        self.assertEqual(self.s_stack.stack[-1], new_item)

    # предусловие: стек не пустой
    # постусловие: из стека удалён верхний элемент
    def test_pop(self):
        # проверка случая с пустым стеком
        # должен вернуть None
        len_stack = len(self.s_stack.stack)
        self.assertEqual(len_stack, 0)
        self.assertIsNone(self.s_stack.pop())
        self.assertEqual(len(self.s_stack.stack), len_stack)
        self.assertEqual(self.s_stack.stack, [])
        # проверка случая с единственным элементом в стеке
        new_item = random.randint(0, 100)
        self.s_stack.push(new_item)
        self.assertEqual(len(self.s_stack.stack), len_stack + 1)
        pop_result = self.s_stack.pop()
        self.assertEqual(pop_result, new_item)
        self.assertEqual(len(self.s_stack.stack), len_stack)
        self.assertEqual(self.s_stack.stack, [])
        # проверка случая с наличием множества элементов в стеке
        number = random.randrange(3, 100)
        items_list = [random.randint(0, 100) for _ in range(number)]
        for item in items_list:
            self.s_stack.push(item)
        pop_result = self.s_stack.pop()
        self.assertEqual(pop_result, items_list[-1])
        self.assertEqual(len(self.s_stack.stack), len(items_list) - 1)
        self.assertListEqual(self.s_stack.stack, items_list[:-1])
        # удаляем все значения из стека
        for _ in range(len(items_list[:-1])):
            self.s_stack.pop()
        self.assertEqual(len(self.s_stack.stack), 0)
        self.assertListEqual(self.s_stack.stack, [])
        self.assertIsNone(self.s_stack.pop())
        self.assertEqual(len(self.s_stack.stack), 0)
        self.assertEqual(self.s_stack.stack, [])

    # предусловие: стек не пустой
    def test_peek(self):
        # проверка случая с пустым стеком
        # должен вернуть None
        len_stack = len(self.s_stack.stack)
        self.assertIsNone(self.s_stack.peek())
        self.assertEqual(len(self.s_stack.stack), len_stack)
        self.assertEqual(self.s_stack.stack, [])
        # проверка случая с единственным элементом в стеке
        new_item = random.randint(0, 100)
        self.s_stack.push(new_item)
        self.assertEqual(len(self.s_stack.stack), len_stack + 1)
        len_stack = len(self.s_stack.stack)
        self.assertEqual(self.s_stack.peek(), self.s_stack.stack[-1])
        self.assertEqual(len(self.s_stack.stack), len_stack)
        self.assertEqual(self.s_stack.stack, [self.s_stack.peek()])
        # проверка случая с наличием множества элементов в стеке
        self.s_stack = Stack()
        number = random.randrange(3, 100)
        items_list = [random.randint(0, 100) for _ in range(number)]
        for item in items_list:
            self.s_stack.push(item)
        self.assertEqual(self.s_stack.peek(), items_list[-1])
        self.assertEqual(len(self.s_stack.stack), len(items_list))
        self.assertListEqual(self.s_stack.stack, items_list)

    def test_size(self):
        self.assertEqual(self.s_stack.size(), len(self.s_stack.stack))
        self.assertEqual(self.s_stack.size(), 0)
        # проверка случая с единственным элементом в стеке
        new_item = random.randint(0, 100)
        self.s_stack.push(new_item)
        self.assertEqual(self.s_stack.size(), len(self.s_stack.stack))
        self.assertEqual(self.s_stack.size(), 1)
        # проверка случая с наличием множества элементов в стеке
        number = random.randrange(3, 100)
        items_list = [random.randint(0, 100) for _ in range(number)]
        for item in items_list:
            self.s_stack.push(item)
        self.assertEqual(self.s_stack.size(), len(self.s_stack.stack))
        self.assertEqual(self.s_stack.size(), len(items_list) + 1)


if __name__ == '__main__':
    unittest.main()
