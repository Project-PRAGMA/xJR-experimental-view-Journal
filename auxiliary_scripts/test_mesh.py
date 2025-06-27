# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2025 Andrzej Kaczmarczyk<droodev@gmail.com>
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the “Software”), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import unittest
import unittest.mock
from tools import Mesh2 as Mesh
from tools import CellsFeatures, CellsStatii, AdaptationDriver


class TestMesh(unittest.TestCase):

    def setUp(self):
        self._votes_count = 100
        self._cov_parts = 100
        self._appr_parts = 100
        self._comm_size = 10
        self._max_pos_appr = self._comm_size * self._votes_count
        self._mesh = Mesh(
            cand_count=100,
            votes_count=self._votes_count,
            comm_size=self._comm_size,
            coverage_parts=self._cov_parts,
            approval_parts=self._appr_parts,
            min_cov=3,
            max_cov=95,
            min_appr=11,
            max_appr=950,
        )

    def test_get_index_by_values(self):
        test_cases = [
            ((0, 0), (0, 0)),
            ((1, 0), (0, 0)),
            ((10, 0), (9, 0)),
            ((11, 0), (10, 0)),
            ((0, 10), (0, 0)),
            ((0, 11), (0, 1)),
            ((55, 123), (54, 12)),
            ((50, 120), (49, 11)),
            ((100, 1000), (99, 99)),
            ((100, 999), (99, 99)),
            ((100, 990), (99, 98)),
            ((99, 990), (98, 98)),
        ]
        for tested_case in test_cases:
            indices = self._mesh.get_index_by_values(
                tested_case[0][0], tested_case[0][1]
            )
            self.assertEqual(indices, (tested_case[1][0], tested_case[1][1]))

    def test_construction_sizes(self):
        self.assertEqual(100, self._mesh.cov_parts)
        self.assertEqual(100, self._mesh.app_parts)
        with self.assertRaises(IndexError):
            self._mesh.get_cell_by_index(100, 100)

    def test_construction(self):
        appr_step = self._max_pos_appr // self._appr_parts
        cov_step = self._votes_count // self._cov_parts
        for cov_index in range(self._cov_parts):
            for app_index in range(self._appr_parts):
                current_cell = self._mesh.get_cell_by_index(cov_index, app_index)
                self.assertEqual(
                    current_cell["app_bounds"],
                    (
                        app_index * appr_step + 1 if app_index != 0 else 0,
                        (app_index + 1) * appr_step,
                    ),
                )
                self.assertEqual(
                    current_cell["cov_bounds"],
                    (
                        cov_index * cov_step + 1 if cov_index != 0 else 0,
                        (cov_index + 1) * cov_step,
                    ),
                )
        cells_properties = {
            (0, 0): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (0, 1): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (0, 99): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (2, 0): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (2, 1): (CellsFeatures.UNKNOWN, CellsStatii.DIRTY),
            (3, 0): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (3, 1): (CellsFeatures.UNKNOWN, CellsStatii.DIRTY),
            (4, 0): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (50, 0): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (95, 0): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (95, 10): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (95, 50): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (94, 1): (CellsFeatures.UNKNOWN, CellsStatii.DIRTY),
            (94, 40): (CellsFeatures.UNKNOWN, CellsStatii.DIRTY),
            (94, 94): (CellsFeatures.UNKNOWN, CellsStatii.DIRTY),
            (10, 96): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (50, 96): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (94, 96): (CellsFeatures.EMPTY, CellsStatii.FIXED),
            (94, 94): (CellsFeatures.UNKNOWN, CellsStatii.DIRTY),
        }
        for cell_indices in cells_properties.keys():
            self.assertEqual(
                self._mesh.get_cell_by_index(*cell_indices)["features"],
                cells_properties[cell_indices][0],
                msg=f"Features; Index: {cell_indices}",
            )
            self.assertEqual(
                self._mesh.get_cell_by_index(*cell_indices)["status"],
                cells_properties[cell_indices][1],
                msg=f"Status; Index: {cell_indices}",
            )

    def _fill_with_one_target_function(self):
        self._mesh.set_computation_area_by_feature(CellsFeatures.UNKNOWN)
        self._target_covs = {25, 26, 27}
        self._target_apps = {258}

        def target_func(min_cov, max_cov, min_app, max_app):
            avail_covs = set(range(min_cov, max_cov + 1))
            avail_apps = set(range(min_app, max_app + 1))
            in_covs = len(self._target_covs & avail_covs) > 0
            in_apps = len(self._target_apps & avail_apps) > 0
            return (in_covs and in_apps), None, 26, 258

        mock_func = unittest.mock.MagicMock(wraps=target_func)
        self._mesh.fill_with(mock_func, CellsFeatures.EXISTS, CellsFeatures.EMPTY)
        self._target_cov_indices = {24, 25, 26}
        self._target_app_index = 25
        return mock_func

    def _fill_with_second_target_function(self):
        self._mesh.set_computation_area_by_feature(CellsFeatures.EXISTS)
        self._target_cov2 = 26
        self._target_app2 = 258

        def target_func(min_cov, max_cov, min_appr, max_appr):
            is_correct_cell = (
                min_cov <= self._target_cov2
                and max_cov >= self._target_cov2
                and min_appr <= self._target_app2
                and max_appr >= self._target_app2
            )
            return is_correct_cell, None, self._target_cov2, self._target_app2

        mock_func = unittest.mock.MagicMock(wraps=target_func)
        self._mesh.fill_with(mock_func, CellsFeatures.JR)
        self._target_cov_index2 = 25
        self._target_app_index2 = 25
        return mock_func

    def test_fill_with_one_target_feature_set(self):
        target_func_mock = self._fill_with_one_target_function()
        for cov in self._target_covs:
            target_cell_features = self._mesh.get_cell_by_index(
                *self._mesh.get_index_by_values(cov, list(self._target_apps)[0])
            )["features"]
        self.assertTrue(target_cell_features & CellsFeatures.EXISTS)
        for cov_index in range(100):
            for app_index in range(100):
                if (
                    cov_index in self._target_cov_indices
                    and app_index is self._target_app_index
                ):
                    continue
                self.assertEqual(
                    self._mesh.get_cell_by_index(cov_index, app_index)["features"],
                    CellsFeatures.EMPTY,
                )
        for call in target_func_mock.call_args_list:
            # This cell computed for broader areas so does not
            # to be recomputed now
            self.assertNotEqual(call, ((26, 26, 251, 260),))
            # A positive result in this cell computer already
            # for a superarea so in this area the result
            # does need to be recomputed
            self.assertNotEqual(call, ((3, 49, 111, 480),))

    def test_fill_with_target_twice_feature_set(self):
        target_func_mock = self._fill_with_one_target_function()
        target_func_mock = self._fill_with_second_target_function()
        target_cell_features = self._mesh.get_cell_by_index(
            *self._mesh.get_index_by_values(self._target_cov2, self._target_app2)
        )["features"]
        self.assertEqual(
            target_cell_features, (CellsFeatures.EXISTS | CellsFeatures.JR)
        )
        for cov_index in range(100):
            for app_index in range(100):
                if (
                    cov_index is self._target_cov_index2
                    and app_index is self._target_app_index2
                ):
                    continue
                self.assertTrue(
                    self._mesh.get_cell_by_index(cov_index, app_index)["features"]
                    in (CellsFeatures.EXISTS | CellsFeatures.EMPTY)
                )
        for call in target_func_mock.call_args_list:
            self.assertNotEqual(
                call, ((self._target_cov2, self._target_cov2, 251, 260),)
            )

    def test_fill_with_one_target_status_set(self):
        self._fill_with_one_target_function()
        for cov_index in range(100):
            for app_index in range(100):
                if (
                    cov_index > 1
                    and cov_index < 95
                    and app_index > 0
                    and app_index < 95
                ):
                    self.assertEqual(
                        self._mesh.get_cell_by_index(cov_index, app_index)["status"],
                        CellsStatii.CLEAN,
                        msg=f"Status should be CLEAN: Index: {(cov_index,app_index)}",
                    )


class TestAdaptationDriver(unittest.TestCase):
    def test_construction(self):
        driver = AdaptationDriver(10, 91, 0, 1000)
        self.assertEqual(driver.get_next_area(), (10, 91, 0, 1000))

    def test_throwing_when_empty(self):
        driver = AdaptationDriver(10, 91, 0, 1000)
        driver.get_next_area()
        with self.assertRaises(IndexError):
            driver.get_next_area()

    def test_bisection_to_four_areas(self):
        driver = AdaptationDriver(10, 91, 0, 1000)
        area = driver.get_next_area()
        driver.bisect_area(area)
        expected_areas = set(
            [
                (10, 50, 0, 500),
                (10, 50, 501, 1000),
                (51, 91, 0, 500),
                (51, 91, 501, 1000),
            ]
        )
        collected_areas = {driver.get_next_area() for _ in range(4)}
        self.assertEqual(collected_areas, expected_areas)

    def test_bisection_to_four_areas_with_by_one_coordinate(self):
        driver = AdaptationDriver(2, 3, 15, 17)
        area = driver.get_next_area()
        driver.bisect_area(area)
        expected_areas = set(
            [(2, 2, 15, 16), (2, 2, 17, 17), (3, 3, 15, 16), (3, 3, 17, 17)]
        )
        collected_areas = {driver.get_next_area() for _ in range(4)}
        self.assertEqual(collected_areas, expected_areas)

    def test_bisection_to_two_areas(self):
        driver = AdaptationDriver(2, 2, 5, 6)
        area = driver.get_next_area()
        driver.bisect_area(area)
        expected_areas = set([(2, 2, 5, 5), (2, 2, 6, 6)])
        collected_areas = {driver.get_next_area() for _ in range(2)}
        self.assertEqual(collected_areas, expected_areas)

    def test_bisection_error_unbisectable_area(self):
        driver = AdaptationDriver(2, 2, 3, 3)
        area = driver.get_next_area()
        with self.assertRaises(ValueError):
            driver.bisect_area(area)


if __name__ == "__main__":
    unittest.main()
