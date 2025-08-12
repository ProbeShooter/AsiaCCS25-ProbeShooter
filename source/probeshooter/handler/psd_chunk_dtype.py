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

import sys
import numpy as np
from typing import Union, Optional
from ..aiming.filter import simple_2d_filter


__all__ = [
    'PSDChunk',
    'PSDChunkSlicesContinuous',
    'PSDChunkSlicesDiscrete'
]


class PSDChunk:
    def __init__(self,
                 identifier: str,
                 psd_chunk: np.ndarray,
                 freq: np.ndarray,
                 metadata: dict
                 ):
        self.original = True
        self.__data = psd_chunk
        self.__freq = freq
        self.__metadata = metadata
        self.__id = identifier
        pass

    def parse_from_freq_range_closed(self,
                                     lower_bound_hz: Optional[Union[float, int]],
                                     upper_bound_hz: Optional[Union[float, int]]
                                     ) -> Optional['PSDChunkSlicesContinuous']:
        assert lower_bound_hz is not None or upper_bound_hz is not None
        if lower_bound_hz is not None and upper_bound_hz is not None:
            selector = (lower_bound_hz <= self.__freq) & (self.__freq <= upper_bound_hz)
        elif lower_bound_hz is not None:
            selector = lower_bound_hz <= self.__freq
        else:  # upper_bound_hz is not None
            selector = self.__freq <= upper_bound_hz
        if np.sum(selector) == 0:
            print("[Warning] 없음.", file=sys.stderr)
            return None
        target_idx = np.argwhere(selector)[:, 0]
        return PSDChunkSlicesContinuous(self.__id,
                                        np.ascontiguousarray(np.copy(self.__data[:, :, target_idx])),
                                        np.ascontiguousarray(np.copy(self.__freq[target_idx])),
                                        self.__metadata,
                                        self)

    def parse_from_nearest_freq_list(self,
                                     target_freq_hz_list: Union[list, tuple, np.ndarray]
                                     ) -> 'PSDChunkSlicesDiscrete':
        assert len(target_freq_hz_list) > 0
        nearset_indices = []
        diff_hz = []
        for t_hz in target_freq_hz_list:
            idx = np.argmin(np.abs(self.__freq - t_hz))
            nearset_indices.append(idx)
            diff_hz.append(np.abs(t_hz - self.__freq[idx]))
            pass
        nearset_indices = np.array(nearset_indices, dtype=np.int32)
        diff_hz = np.array(diff_hz, dtype=np.float64)
        if np.sum(nearset_indices == 0) > 0 or np.sum(nearset_indices == len(self.__freq) - 1) > 0:
            print("[Warning] The frequency of the edge has been selected.", file=sys.stderr)
        return PSDChunkSlicesDiscrete(self.__id,
                                      np.ascontiguousarray(np.copy(self.__data[:, :, nearset_indices])),
                                      np.ascontiguousarray(np.copy(self.__freq[nearset_indices])),
                                      self.__metadata,
                                      self,
                                      diff_hz)

    def parse_from_idx_range_closed(self,
                                    lower_bound_idx: Optional[int],
                                    upper_bound_idx: Optional[int]
                                    ) -> 'PSDChunkSlicesContinuous':
        assert lower_bound_idx is not None or upper_bound_idx is not None
        if lower_bound_idx is not None and upper_bound_idx is not None:
            assert 0 <= lower_bound_idx < upper_bound_idx <= len(self.__freq)
            result_data = np.ascontiguousarray(np.copy(self.__data[:, :, lower_bound_idx:upper_bound_idx+1]))
            result_freq = np.ascontiguousarray(np.copy(self.__freq[lower_bound_idx:upper_bound_idx+1]))
        elif lower_bound_idx is not None:
            assert 0 <= lower_bound_idx
            result_data = np.ascontiguousarray(np.copy(self.__data[:, :, lower_bound_idx:]))
            result_freq = np.ascontiguousarray(np.copy(self.__freq[lower_bound_idx:]))
        else:  # upper_bound_hz is not None
            assert upper_bound_idx <= len(self.__freq)
            result_data = np.ascontiguousarray(np.copy(self.__data[:, :, :upper_bound_idx+1]))
            result_freq = np.ascontiguousarray(np.copy(self.__freq[:upper_bound_idx+1]))
        return PSDChunkSlicesContinuous(self.__id,
                                        result_data,
                                        result_freq,
                                        self.__metadata,
                                        self)
        pass

    def parse_from_idx_list(self,
                            target_idx_list
                            ) -> 'PSDChunkSlicesDiscrete':
        target_idx_list = np.array(target_idx_list, dtype=np.int32)
        new_slice_len = len(target_idx_list)
        err_cnt = np.sum((target_idx_list < 0) | (target_idx_list >= len(self.__freq)))
        assert err_cnt == 0, "ERRORRRRRRRRRR"
        return PSDChunkSlicesDiscrete(self.__id,
                                      np.ascontiguousarray(np.copy(self.__data[:, :, target_idx_list])),
                                      np.ascontiguousarray(np.copy(self.__freq[target_idx_list])),
                                      self.__metadata,
                                      self,
                                      np.full(fill_value=0, shape=(new_slice_len, ), dtype=np.float64))

    def convert_to_dbm_scale(self, correction: int = 30) -> 'PSDChunk':
        r = PSDChunk(self.__id, 10 * np.log10(self.__data) + correction, self.__freq, self.__metadata)
        r.original = False
        return r

    def convert_to_2d_filtered_maps(self,
                                    filter_type: str,
                                    filter_size_xy: (int, int),
                                    verbose: bool = False
                                    ) -> 'PSDChunk':
        filtered_psd_chunk = np.empty_like(self.__data)
        for f_idx in range(len(self.__freq)):
            filtered_psd_chunk[:, :, f_idx] = simple_2d_filter(self.data[:, :, f_idx], filter_type, filter_size_xy)
            if verbose and (f_idx + 1) % 100 == 0:
                print(f"{f_idx + 1}/{len(self.__freq)} Completed.")
        else:
            if verbose:
                print(f"{len(self.__freq)}/{len(self.__freq)} Completed.")
        r = PSDChunk(self.__id, filtered_psd_chunk, self.__freq, self.__metadata)
        r.original = False
        return r

    @property
    def data(self):
        return self.__data

    @property
    def freq(self):
        return self.__freq

    @property
    def metadata(self):
        return self.__metadata

    @property
    def shape(self):
        return self.__data.shape

    @property
    def x_div(self):
        return self.__data.shape[1]

    @property
    def y_div(self):
        return self.__data.shape[0]

    @property
    def bins(self):
        return self.__data.shape[2]

    @property
    def rbw(self):
        return self.__metadata['rbw']

    @property
    def vbw(self):
        return self.__metadata['vbw']

    @property
    def point_to_point_diff_hz(self):
        return self.__metadata['freq_span'] / self.__data.shape[2]

    @property
    def n_slices(self):
        return len(self.__freq)

    def __repr__(self):
        return self.__id
    pass


class PSDChunkSlicesContinuous(PSDChunk):
    def __init__(self,
                 identifier: str,
                 psd_chunk: np.ndarray,
                 freq: np.ndarray,
                 metadata: dict,
                 parent: PSDChunk):
        super().__init__(identifier, psd_chunk, freq, metadata)
        self.original = False
        self.parent = parent
        pass

    def __repr__(self):
        return '[Slice-C] ' + super().__repr__()
    pass


class PSDChunkSlicesDiscrete(PSDChunk):
    def __init__(self,
                 identifier: str,
                 psd_chunk: np.ndarray,
                 freq: np.ndarray,
                 metadata: dict,
                 parent: PSDChunk,
                 diff_hz_list: np.ndarray):
        super().__init__(identifier, psd_chunk, freq, metadata)
        self.original = False
        self.parent = parent,
        self.diff_hz_list = diff_hz_list
        pass

    def __repr__(self):
        return '[Slice-D] ' + super().__repr__()
    pass
