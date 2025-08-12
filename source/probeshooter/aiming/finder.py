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
from scipy.ndimage import maximum_filter, generate_binary_structure, binary_erosion
from typing import Union, Optional


__all__ = [
    'calc_top_n_percentile_value',
    'calc_n_percent_value_of_global_maxima',
    'find_local_maxima_loc_2d',
    'find_top_n_percent_loc_2d'
]


def calc_top_n_percentile_value(target_arr: np.ndarray,
                                percentile: float
                                ) -> Union[float, int]:
    assert 0 <= percentile <= 1
    flat_arr = target_arr.flatten()
    sorted_flat_arr = np.sort(flat_arr)
    top_n_percentile_index = int(np.ceil((percentile * len(sorted_flat_arr))))
    closest_value = sorted_flat_arr[top_n_percentile_index]
    return float(closest_value)


def calc_n_percent_value_of_global_maxima(target_arr: np.ndarray,
                                          percent: float
                                          ) -> Union[float, int]:
    assert 0 <= percent <= 1
    max_val = np.max(target_arr)
    return max_val * percent


def find_local_maxima_loc_2d(arr_2d: Union[np.ndarray, list, tuple],
                             threshold: Optional[Union[float, int]] = None
                             ) -> np.ndarray:
    neighborhood = generate_binary_structure(2, 2)
    local_max = maximum_filter(arr_2d, footprint=neighborhood) == arr_2d
    background = (arr_2d == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)
    detected_maxima = local_max ^ eroded_background
    if threshold is not None:
        detected_maxima = detected_maxima & (arr_2d > threshold)
    return np.argwhere(detected_maxima)[:, [1, 0]]


def find_top_n_percent_loc_2d(target_arr: np.ndarray,
                              percentile: float
                              ) -> np.ndarray:
    top_n_percentile_index = calc_top_n_percentile_value(target_arr, percentile)
    return np.argwhere(target_arr >= top_n_percentile_index)[:, [1, 0]]
