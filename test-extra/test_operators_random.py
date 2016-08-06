# Copyright (C) 2016 East Asian Observatory.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from random import sample
from unittest import TestCase

from pymoc import MOC


class OperatorsRandomizedTestCase(TestCase):
    def test_operators(self):
        repeats = 10
        order = 6

        for i in range(0, repeats):
            # Make random MOCs, take difference and intersection.
            p = self._make_random_moc(order)
            q = self._make_random_moc(order)

            s_pq = p - q
            s_qp = q - p
            i_pq = p.intersection(q)
            i_qp = q.intersection(p)

            # p.write('test_moc_p_{}.fits'.format(i + 1), clobber=True)
            # q.write('test_moc_q_{}.fits'.format(i + 1), clobber=True)
            # s_pq.write('test_moc_pq_{}.fits'.format(i + 1), clobber=True)
            # s_qp.write('test_moc_qp_{}.fits'.format(i + 1), clobber=True)
            # i_pq.write('test_moc_i_{}.fits'.format(i + 1), clobber=True)

            # Intersection should be the same both ways round.
            self.assertEqual(i_pq, i_qp)

            # Areas should add up to differences + 2 x intersection.
            self.assertAlmostEqual(p.area + q.area,
                                   s_pq.area + s_qp.area + 2 * i_pq.area,
                                   places=10)

            # Make differences and intersection via flattened set.
            p_flat = p.flattened(order=order)
            q_flat = q.flattened(order=order)

            s_pq_flat = p_flat - q_flat
            s_qp_flat = q_flat - p_flat
            i_flat = p_flat & q_flat

            # Compare with flattened-method version via MOC equality.
            self.assertEqual(s_pq, MOC(order, s_pq_flat))
            self.assertEqual(s_qp, MOC(order, s_qp_flat))
            self.assertEqual(i_pq, MOC(order, i_flat))

            # Compare with flattened-method version via flat set.
            s_pq_flattened = s_pq.flattened(order=order)
            s_qp_flattened = s_qp.flattened(order=order)
            i_pq_flattened = i_pq.flattened(order=order)
            i_qp_flattened = i_qp.flattened(order=order)

            self.assertEqual(s_pq_flattened, s_pq_flat)
            self.assertEqual(s_qp_flattened, s_qp_flat)
            self.assertEqual(i_pq_flattened, i_flat)
            self.assertEqual(i_qp_flattened, i_flat)

            # Differences and intersection should be disjoint.
            self.assertTrue(s_pq_flattened.isdisjoint(s_qp_flattened))
            self.assertTrue(s_pq_flattened.isdisjoint(i_pq_flattened))
            self.assertTrue(s_qp_flattened.isdisjoint(i_pq_flattened))

    def _make_random_moc(self, order):
        m = MOC()

        for order_i in range(0, order + 1):
            m.add(order_i, sample(range(0, 12 * 4 ** order_i), 4 ** order_i))

        return m
