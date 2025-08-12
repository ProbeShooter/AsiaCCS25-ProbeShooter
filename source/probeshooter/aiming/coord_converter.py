#  Copyright (c) 2025 Daehyeon Bae
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import numpy as np
from typing import Tuple, Union


__all__ = [
    'convert_to_real_location',
    'convert_to_mm_location_from_origin'
]


def convert_to_real_location(reference_arr_2d: np.ndarray,
                             pseudo_point_xy: Union[np.ndarray, Tuple[Union[float, int], Union[float, int]]],
                             real_point_left_top_xy: Tuple[Union[float, int], Union[float, int]],
                             real_point_right_bottom_xy: Tuple[Union[float, int], Union[float, int]],
                             apply_round: bool = True
                             ):
    assert len(reference_arr_2d.shape) == 2
    assert 0 <= pseudo_point_xy[0] <= reference_arr_2d.shape[1]
    assert 0 <= pseudo_point_xy[1] <= reference_arr_2d.shape[0]
    distance_xy = (real_point_right_bottom_xy[0] - real_point_left_top_xy[0],
                   real_point_right_bottom_xy[1] - real_point_left_top_xy[1])
    div_x = reference_arr_2d.shape[1]
    div_y = reference_arr_2d.shape[0]
    unit_x = distance_xy[0] / div_x
    unit_y = distance_xy[1] / div_y
    real_x = real_point_left_top_xy[0] + unit_x * pseudo_point_xy[0]
    real_y = real_point_left_top_xy[1] + unit_y * pseudo_point_xy[1]
    if apply_round:
        real_x = int(real_x)
        real_y = int(real_y)
    return real_x, real_y


def convert_to_mm_location_from_origin(reference_arr_2d: np.ndarray,
                                       pseudo_point_xy: Union[np.ndarray, Tuple[Union[float, int], Union[float, int]]],
                                       chip_mm_xy: Tuple[Union[float, int], Union[float, int]],):
    real_x, real_y = convert_to_real_location(reference_arr_2d,
                                              pseudo_point_xy,
                                              (0, 0),
                                              chip_mm_xy,
                                              apply_round=False)
    return real_x, real_y
