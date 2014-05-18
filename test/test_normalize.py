from unittest import TestCase

from pymoc import MOC

class NormalizeTestCase(TestCase):
    def test_aggregate(self):
        m = MOC(10, set([0, 1, 2, 3, 4]))

        self.assertEqual(m.order, 10)
        self.assertEqual(m[10], frozenset([0, 1, 2, 3, 4]))
        self.assertEqual(m[9], frozenset())

        m.normalize()

        self.assertEqual(m.order, 10)
        self.assertEqual(m[10], frozenset([4]))
        self.assertEqual(m[9], frozenset([0]))

    def test_included(self):
        m = MOC(10, set([0, 1, 2, 3, 4]))

        m.add(8, set([0]))

        self.assertEqual(m.order, 10)
        self.assertEqual(m[8], frozenset([0]))
        self.assertEqual(m[9], frozenset())
        self.assertEqual(m[10], frozenset([0, 1, 2, 3, 4]))

        m.normalize()

        self.assertEqual(m.order, 8)
        self.assertEqual(m[8], frozenset([0]))
        self.assertEqual(m[9], frozenset())
        self.assertEqual(m[10], frozenset())
