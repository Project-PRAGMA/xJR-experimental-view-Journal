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

import collections
import time

import core.mylog

logger = core.mylog.get_logger()


def committeApprovalAndCoverage(candidates, voters, committee):
    commSet = set(committee)
    coverageCounter = 0
    for voter in voters.values():
        if len(commSet & set(voter)) > 0:
            coverageCounter = coverageCounter + 1
    approvalCounter = 0
    for cand in committee:
        for voter in voters.values():
            if cand in voter:
                approvalCounter = approvalCounter + 1
    return coverageCounter, approvalCounter


def loadPrefLibPartialOrder(filepath, groupsApproved):
    profile = {}
    multiplicities = {}
    with open(filepath, "r") as infile:
        counter = 0
        votersnr = None
        candnr = None
        for line in infile:
            counter = counter + 1
            if counter == 1:
                candnr = int(line.strip())
                continue
            if counter > 1 and counter <= candnr + 1:
                continue
            if counter == candnr + 2:
                votersnr = int(line.strip().split(",")[0])
                continue
            lineparts = line.strip().split(",")
            multiplicity = int(lineparts[0])
            groups = {}
            partnr = 1
            #      print lineparts
            while partnr <= len(lineparts[1:]):
                part = lineparts[partnr]
                if part == "{}" or part == "":
                    groupApproved = []
                elif part.startswith("{"):
                    endpartnr = partnr
                    while not lineparts[endpartnr].endswith("}"):
                        endpartnr = endpartnr + 1
                    groupApproved = reduce(
                        lambda acc, elem: acc + [int(elem) - 1],
                        (",".join(lineparts[partnr : endpartnr + 1])[1:-1]).split(","),
                        [],
                    )
                    partnr = endpartnr
                else:
                    groupApproved = [int(part) - 1]
                groups[len(groups)] = groupApproved
                partnr = partnr + 1

            approved = reduce(
                lambda acc, elem: acc + elem,
                [g for gnr, g in groups.items() if gnr < groupsApproved],
                [],
            )

            nextVoteNr = len(profile)
            profile[nextVoteNr] = approved
            multiplicities[nextVoteNr] = multiplicity
    return profile, range(candnr), multiplicities


from enum import Flag, auto, Enum


class CellsFeatures(Flag):
    UNKNOWN = 0
    EMPTY = auto()
    EXISTS = auto()
    JR = auto()
    PJR = auto()
    EJR = auto()
    PAV = auto()
    PHR = auto()


default_features_ordered_mapping = [
    (CellsFeatures.UNKNOWN, "u"),
    (CellsFeatures.EMPTY, "."),
    (CellsFeatures.EXISTS, "s"),
    (CellsFeatures.JR, "x"),
    (CellsFeatures.PJR, "r"),
    (CellsFeatures.EJR, "e"),
    (CellsFeatures.PAV, "v"),
    (CellsFeatures.PHR, "p"),
]


class CellsStatii(Enum):
    DIRTY = 0
    CLEAN = auto()
    FIXED = auto()


class Mesh2(object):
    def __init__(
        self,
        cand_count,
        votes_count,
        comm_size,
        coverage_parts,
        approval_parts,
        min_cov,
        max_cov,
        min_appr,
        max_appr,
    ):
        self._cov_parts = coverage_parts
        self._app_parts = approval_parts
        self._maxApproval = comm_size * votes_count
        self._maxCoverage = votes_count
        self._initialize_cells(
            votes_count, comm_size * votes_count, coverage_parts, approval_parts
        )
        min_corner_index, max_corner_index = self._preset_properties(
            min_cov, max_cov, min_appr, max_appr
        )

    @property
    def cov_parts(self):
        return self._cov_parts

    @property
    def app_parts(self):
        return self._app_parts

    def set_computation_area_by_feature(self, feature):
        min_cov_index = self._find_extreme_cov_by_feature(feature)
        max_cov_index = self._find_extreme_cov_by_feature(feature, False)
        min_app_index = self._find_extreme_app_by_feature(feature)
        max_app_index = self._find_extreme_app_by_feature(feature, False)
        self._adaptation_driver = AdaptationDriver(
            min_cov_index, max_cov_index, min_app_index, max_app_index
        )

    def _find_extreme_cov_by_feature(self, feature, find_min=True):
        cov_indices = range(self.cov_parts)
        for cov_index in cov_indices if find_min else reversed(cov_indices):
            for app_index in range(self.app_parts):
                curr_cell_feature = self.get_cell_by_index(cov_index, app_index)[
                    "features"
                ]
                if self._check_flag_or_empty(curr_cell_feature, feature):
                    return cov_index
        raise ValueError("No cell with requested feature")

    def _find_extreme_app_by_feature(self, feature, find_min=True):
        app_indices = range(self.app_parts)
        for app_index in app_indices if find_min else reversed(app_indices):
            for cov_index in range(self.cov_parts):
                curr_cell_feature = self.get_cell_by_index(cov_index, app_index)[
                    "features"
                ]
                if self._check_flag_or_empty(curr_cell_feature, feature):
                    return app_index
        raise ValueError("No cell with requested feature")

    def _check_flag_or_empty(self, present, pattern):
        # formula after "or" allows for testing for an empty flag
        return (present & pattern) or (present is pattern)

    def _initialize_cells(
        self, max_coverage, max_approval, coverage_parts, approval_parts
    ):
        if max_coverage % coverage_parts != 0:
            raise KeyError("An equal partition of coverage in a mesh impossible")
        if max_approval % approval_parts != 0:
            raise KeyError("An equal partition of approval in a mesh impossible")
        self._coverage_step = max_coverage // coverage_parts
        self._approval_step = max_approval // approval_parts
        coverageRanges = self._compute_ranges(
            0, max_coverage, self._coverage_step, coverage_parts
        )
        approvalRanges = self._compute_ranges(
            0, max_approval, self._approval_step, approval_parts
        )
        self._cells_array = []
        for cov_bounds in coverageRanges:
            self._cells_array.append([])
            for app_bounds in approvalRanges:
                self._cells_array[-1].append(
                    {
                        "app_bounds": app_bounds,
                        "cov_bounds": cov_bounds,
                        "features": CellsFeatures.UNKNOWN,
                        "status": CellsStatii.DIRTY,
                    }
                )

    def get_cell_by_index(self, cov_index, app_index):
        return self._cells_array[cov_index][app_index]

    def _compute_ranges(self, min_val, max_val, step, force_for_unequal_division=False):
        def _compensate_assymetry_of_zero(lower_bound):
            return lower_bound + 1 if lower_bound > 0 else lower_bound

        lower_bounds = range(min_val, max_val, step)
        ranges = [
            (_compensate_assymetry_of_zero(lower_bound), lower_bound + step)
            for lower_bound in lower_bounds
        ]
        if force_for_unequal_division:
            ## This code mitigates unequal division of max_val/parts.
            ## Even though, calling this function internally from the class,
            ## we do not allow for such situations.
            if ranges[-1][1] != max_val:
                ranges[-1] = (ranges[-1][0], max_val)
        return ranges

    def _preset_properties(self, min_cov, max_cov, min_appr, max_appr):
        min_corner = self.get_index_by_values(min_cov, min_appr)
        max_corner = self.get_index_by_values(max_cov, max_appr)
        empty_cov_indices = [
            index
            for index in range(self.cov_parts)
            if index < min_corner[0] or index > max_corner[0]
        ]
        empty_apr_indices = [
            index
            for index in range(self.app_parts)
            if index < min_corner[1] or index > max_corner[1]
        ]
        for cov_index in range(len(self._cells_array)):
            for app_index in range(len(self._cells_array[cov_index])):
                if (
                    cov_index < min_corner[0]
                    or cov_index > max_corner[0]
                    or app_index < min_corner[1]
                    or app_index > max_corner[1]
                ):
                    self._cells_array[cov_index][app_index][
                        "features"
                    ] = CellsFeatures.EMPTY
                    self._cells_array[cov_index][app_index][
                        "status"
                    ] = CellsStatii.FIXED
        return min_corner, max_corner

    def get_index_by_values(self, coverage, approval):
        for cov_index in range(len(self._cells_array)):
            for app_index in range(len(self._cells_array[cov_index])):
                current_cell_cov_bounds = self._cells_array[cov_index][app_index][
                    "cov_bounds"
                ]
                current_cell_app_bounds = self._cells_array[cov_index][app_index][
                    "app_bounds"
                ]
                if (
                    coverage >= current_cell_cov_bounds[0]
                    and coverage <= current_cell_cov_bounds[1]
                    and approval >= current_cell_app_bounds[0]
                    and approval <= current_cell_app_bounds[1]
                ):
                    return (cov_index, app_index)

    def is_feature_in_area(
        self, min_cov_index, max_cov_index, min_app_index, max_app_index, feature
    ):
        for cov in range(min_cov_index, max_cov_index + 1):
            for app in range(min_app_index, max_app_index + 1):
                if self.get_cell_by_index(cov, app)["features"] & feature:
                    return True
        return False

    def fill_with(self, functor, succ_feature, fail_feature=None):
        """If functor returns True for given bounds which cannot
        be bisected more, then succ_feature is *added* to the
        features flag. If functor returns False for such bounds,
        then the features flag is *set* to fail_feature; unless
        the latter is None"""
        computed_areas = -1
        cumulative_time = 0
        start_time = time.time()
        current_time = None
        try:
            while True:
                computed_areas += 1
                cumulative_time = time.time() - start_time
                if computed_areas > 0 and (computed_areas % 250 == 0):
                    logger.info(
                        f"Areas:{computed_areas} Tot "
                        f"time: {round(cumulative_time,2)}s Avg time:"
                        f"{round(cumulative_time/computed_areas,2)}"
                    )
                area = self._adaptation_driver.get_next_area()
                min_cov_index, max_cov_index, min_app_index, max_app_index = area
                min_cell = self.get_cell_by_index(min_cov_index, min_app_index)
                max_cell = self.get_cell_by_index(max_cov_index, max_app_index)
                if (min_cell == max_cell) and (min_cell["features"] & succ_feature):
                    continue
                is_success = self.is_feature_in_area(*area, succ_feature)
                # is_success = False
                success_computed = False
                if not is_success:
                    functor_ret = functor(
                        min_cell["cov_bounds"][0],
                        max_cell["cov_bounds"][1],
                        min_cell["app_bounds"][0],
                        max_cell["app_bounds"][1],
                    )
                    is_success = functor_ret[0]
                    success_computed = True
                bounds = (
                    min_cell["cov_bounds"][0],
                    max_cell["cov_bounds"][1],
                    min_cell["app_bounds"][0],
                    max_cell["app_bounds"][1],
                )
                logger.debug(f"{bounds}: {is_success}")
                if is_success:
                    if min_cell == max_cell:
                        min_cell["features"] |= succ_feature
                        min_cell["status"] = CellsStatii.CLEAN
                    else:
                        if success_computed:
                            cov_val, app_val = functor_ret[2], functor_ret[3]
                            computed_cell = self.get_cell_by_index(
                                *self.get_index_by_values(cov_val, app_val)
                            )
                            computed_cell["features"] |= succ_feature
                            computed_cell["status"] = CellsStatii.CLEAN
                        self._adaptation_driver.bisect_area(area)
                else:
                    for cov_index in range(min_cov_index, max_cov_index + 1):
                        for app_index in range(min_app_index, max_app_index + 1):
                            current_cell = self.get_cell_by_index(cov_index, app_index)
                            current_cell["status"] = CellsStatii.CLEAN
                            if fail_feature:
                                current_cell["features"] = fail_feature
        except IndexError:
            pass

    def depict(self, outStream):
        for cov_index in reversed(range(self.cov_parts)):
            for app_index in range(self.app_parts):
                current_cell = self.get_cell_by_index(cov_index, app_index)
                for concept_mapping in reversed(default_features_ordered_mapping):
                    if current_cell["features"] & concept_mapping[0]:
                        outStream.write(concept_mapping[1])
                        break
            outStream.write("\n")


class AdaptationDriver(object):
    def __init__(self, min_x, max_x, min_y, max_y):
        self._computation_tree = collections.deque()
        self._computation_tree.append((min_x, max_x, min_y, max_y))

    def get_next_area(self):
        return self._computation_tree.popleft()

    def bisect_area(self, area):
        min_x, max_x, min_y, max_y = area
        if min_x == max_x and min_y == max_y:
            raise ValueError("Area cannot be bisected")
        new_cov_areas = self._bisect_segment(min_x, max_x)
        new_app_areas = self._bisect_segment(min_y, max_y)
        for new_cov_area in new_cov_areas:
            for new_app_area in new_app_areas:
                self._computation_tree.append(new_cov_area + new_app_area)

    def _bisect_segment(self, min_val, max_val):
        if min_val == max_val:
            return ((min_val, max_val),)
        midpoint = (min_val + max_val) // 2
        return (min_val, midpoint), (midpoint + 1, max_val)


class Mesh(object):

    def _computeRanges(self, minVal, maxVal, parts):
        step = maxVal // parts
        lowerBounds = range(minVal, maxVal + 1, step)
        ranges = [(lowerBound, lowerBound + step - 1) for lowerBound in lowerBounds]
        if ranges[-1][1] != maxVal:
            ranges[-1] = (ranges[-1][0], maxVal)
        return ranges

    def _initializeCells(self):
        coverageRanges = self._computeRanges(1, self._maxCoverage, self.coverageParts)
        approvalRanges = self._computeRanges(1, self._maxApproval, self.approvalParts)
        self._cells = {
            cR + aR: self._initVal for cR in coverageRanges for aR in approvalRanges
        }
        self._cellStatus = {cell: True for cell in self._cells}

    def _initializeCellsCoordinates(self):
        """Starting from 1 (not from 0)"""
        self._cellCoordinate = {}
        colCounter = 0
        rowCounter = self.coverageParts
        for cell in self._sortCells_Fragile(self._cells):
            self._cellCoordinate[cell] = (rowCounter, colCounter + 1)
            colCounter = (colCounter + 1) % self.approvalParts
            if colCounter == 0:
                rowCounter = rowCounter - 1

    def _sortCells_Fragile(self, cells):
        return sorted(cells, key=lambda cell: (-cell[0], cell[2]))

    def _sortCells(self, cells):
        return self._sortCells_Fragile(cells)

    def getClippedCells(self):
        return self._sortCells([c for c in self._cells if self._cellStatus[c] is False])

    def getUnclippedCells(self):
        return self._sortCells([c for c in self._cells if self._cellStatus[c] is True])

    def getAllCells(self):
        return self._sortCells(self._cells)

    def setValueOfCell(self, cell, value):
        self._cells[cell] = value

    def getValueOfCell(self, cell, value):
        return self._cells[cell]

    def findAndSetValue(self, coverage, approval, value):
        cell = self.getCellFromValues(coverage, approval)
        self.setValueOfCell(cell, value)

    def getCellFromValues(self, coverage, approval):
        for cell in self._cells.keys():
            cCLB, cCUB, cALB, cAUB = cell
            if (
                cCLB <= coverage
                and cCUB >= coverage
                and cALB <= approval
                and cAUB >= approval
            ):
                return cell

    def getCellCoordinate(self, cell):
        return self._cellCoordinate[cell]

    def clipCell(self, cell):
        self._cellStatus[cell] = False

    def unclipCell(self, cell):
        self._cellStatus[cell] = True

    def clipMesh(self, fromDownC, fromUpC, fromDownA, fromUpA):
        for cell, coordinate in self._cellCoordinate.items():
            covCoor, appCoor = coordinate
            if (
                covCoor <= fromDownC
                or covCoor + fromUpC > self.coverageParts
                or appCoor <= fromDownA
                or appCoor + fromUpA > self.approvalParts
            ):
                self.clipCell(cell)

    def clipMeshByValues(self, minC, maxC, minApp, maxApp):
        for cell in self._cells.keys():
            cCLB, cCUB, cALB, cAUB = cell
            if cCUB < minC or cCLB > maxC or cAUB < minApp or cALB > maxApp:
                self.clipCell(cell)

    def depict(self, outStream):
        columnCounter = 0
        for cell in self.getAllCells():
            outStream.write(str(self._cells[cell]))
            columnCounter = (columnCounter + 1) % self.approvalParts
            if columnCounter == 0:
                outStream.write("\n")

    def __init__(
        self,
        candidatesNr,
        votersNr,
        committeeSize,
        coverageParts,
        approvalParts,
        initVal=".",
    ):
        self.candidatesNr = candidatesNr
        self.committeeSize = committeeSize
        self.coverageParts = coverageParts
        self.approvalParts = approvalParts
        self.votersNr = votersNr
        self._initVal = initVal
        self._maxApproval = committeeSize * votersNr
        self._maxCoverage = votersNr
        self._initializeCells()
        self._initializeCellsCoordinates()


def getMultiplicity(vnr, multiplicities):
    if vnr in multiplicities.keys():
        return multiplicities[vnr]
    return 1


def checkIfNLarge2CohesiveGroupExists(
    voters, candidates, committeeSize, N=1, multiplicities={}
):
    votersnr = reduce(
        lambda acc, a: acc + a,
        [getMultiplicity(vnr, multiplicities) for vnr, vote in voters.items()],
        0,
    )
    exists = False
    candpairs = [(c1, c2) for c1 in candidates for c2 in candidates if c1 < c2]
    for c1, c2 in candpairs:
        commonCounter = 0
        for vnr, v in voters.items():
            commonCounter = (
                commonCounter + getMultiplicity(vnr, multiplicities)
                if (c1 in v and c2 in v)
                else 0
            )
        if commonCounter >= N * (float(votersnr) / committeeSize):
            exists = True
    return exists


def checkIf1Large2CohesiveGroupExists(
    voters, candidates, committeeSize, multiplicities={}
):
    return checkIfNLarge2CohesiveGroupExists(
        voters, candidates, committeeSize, 1, multiplicities
    )


def checkIf2Large2CohesiveGroupExists(
    voters, candidates, committeeSize, multiplicities={}
):
    return checkIfNLarge2CohesiveGroupExists(
        voters, candidates, committeeSize, 2, multiplicities
    )
