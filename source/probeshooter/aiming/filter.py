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
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:

import numpy as np
from typing import Union
from scipy.ndimage import minimum_filter1d, maximum_filter1d, uniform_filter1d, median_filter
from scipy.ndimage import minimum_filter, maximum_filter, uniform_filter


__all__ = [
    'convert_1d_filter_size_from_freq',
    'simple_1d_filter',
    'simple_2d_filter',
    'get_2d_binary_mask_from_pts'
]


def convert_1d_filter_size_from_freq(required_window_size_hz: Union[float, int],
                                     point_to_point_diff_hz: Union[float, int]
                                     ) -> int:
    r = required_window_size_hz / point_to_point_diff_hz
    if round(r) % 2 == 1:
        return round(r)
    elif r % 1 < 0.5:
        return round(r) + 1
    else:
        return round(r) - 1
    pass


def simple_1d_filter(target_1d_arr: np.ndarray,
                     filter_type: str,
                     filter_size: int,
                     padding_mode: str = 'nearest'
                     ) -> np.ndarray:
    assert filter_type in ['min', 'median', 'max', 'mean'], "Not supported 'filter_type'."
    if filter_type == 'min':
        return minimum_filter1d(target_1d_arr, filter_size, mode=padding_mode)
    elif filter_type == 'max':
        return maximum_filter1d(target_1d_arr, filter_size, mode=padding_mode)
    elif filter_type == 'mean':
        return uniform_filter1d(target_1d_arr, filter_size, mode=padding_mode)
    elif filter_type == 'median':
        return median_filter(target_1d_arr, filter_size, mode=padding_mode)
    else:
        assert False
    pass


def simple_2d_filter(target_2d_arr: np.ndarray,
                     filter_type: str,
                     filter_size_xy: (int, int),
                     padding_mode: str = 'nearest'
                     ) -> np.ndarray:
    assert filter_type in ['min', 'median', 'max', 'mean'], "Not supported 'filter_type'."
    if filter_type == 'min':
        return minimum_filter(target_2d_arr, (filter_size_xy[1], filter_size_xy[0]), mode=padding_mode)
    elif filter_type == 'max':
        return maximum_filter(target_2d_arr, (filter_size_xy[1], filter_size_xy[0]), mode=padding_mode)
    elif filter_type == 'mean':
        return uniform_filter(target_2d_arr, (filter_size_xy[1], filter_size_xy[0]), mode=padding_mode)
    elif filter_type == 'median':
        return median_filter(target_2d_arr, (filter_size_xy[1], filter_size_xy[0]), mode=padding_mode)
    else:
        assert False
    pass


def get_2d_binary_mask_from_pts(reference_2d_arr: np.ndarray,
                                points_xy_list: Union[np.ndarray, list, tuple]
                                ) -> np.ndarray:
    r = np.zeros_like(reference_2d_arr, dtype=np.bool_)
    for x, y in points_xy_list:
        r[y, x] = True
    return r
