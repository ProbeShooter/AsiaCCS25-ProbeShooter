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

import os
import numpy as np
from typing import Union
from .psd_chunk_dtype import PSDChunk


__all__ = [
    'load_psd_chunk',
    'rotate_psd_chunk',
    'convert_watt_to_dbm'
]


def load_psd_chunk(dataset_path: str,
                   rotate_90d: int = 0,
                   verbose: bool = True
                   ) -> PSDChunk:
    psd_chunk = np.load(f"{dataset_path}{os.sep}psd_chunk.npy")
    psd_chunk = rotate_psd_chunk(psd_chunk, rotate_90d)
    psd_chunk_freq = np.load(f"{dataset_path}{os.sep}freq.npy")
    try:
        with open(f"{dataset_path}{os.sep}meta.txt", 'r') as fp:
            r = fp.readline().strip()
            metadata = eval(r)
            identifier = dataset_path.split(os.sep)[-1]
            if verbose:
                print(f"=================================================================")
                print(f"[ PSD Chunk File ] - {identifier}\n")
                print(f"* Frequency Range  : {metadata['freq_start']}Hz ~ {metadata['freq_stop']}Hz "
                      f"(={metadata['freq_start'] / 1e6:.6f}MHz ~ {metadata['freq_stop'] / 1e6:.6f}MHz)")
                print(f"* Frequency Span   : {metadata['freq_span']}Hz "
                      f"(={metadata['freq_span'] / 1e6:.6f}MHz)")
                print(f"* Center frequency : {metadata['freq_center']}Hz "
                      f"(={metadata['freq_center'] / 1e6:.6f}MHz)")
                print(f"* Resolution BW    : {metadata['rbw']}Hz "
                      f"(={metadata['rbw'] / 1e3:.3f}kHz, ={metadata['rbw'] / 1e6:.6f}MHz)")
                print(f"* View BW          : {metadata['vbw']}Hz "
                      f"(={metadata['vbw'] / 1e3:.3f}kHz, ={metadata['vbw'] / 1e6:.6f}MHz)")
                if 'bin' in metadata:  # backward compatibility
                    print(f"* Bins             : {metadata['bin']:,}")
                if 'bins' in metadata:  # backward compatibility
                    print(f"* Bins             : {metadata['bins']:,}")
                print(f"* Unit             : {metadata['psd_unit']}")
                print(f"* Ref. Level       : {metadata['ref_level']}{metadata['psd_unit']}")
                print(f"* Averaged         : {metadata['avg']}")
                print(f"* Max-Holded       : {metadata['maxh']}")
                print(f"* Avg/Max-H. Cnt.  : {metadata['avg_maxh_count']}")
                print(f"* Sweep Time       : {metadata['sweep_time_s']}s (={metadata['sweep_time_ms']}ms)")
                if 'duration_s' in metadata:  # backward compatibility
                    print(f"* Acq. Duration    : {metadata['duration_s']:.2f}s (={metadata['duration_s']/60:.2f}m)")
                print(f"* Chunk size       : {psd_chunk.nbytes / 1e9:.3f}GiB")
                print(f"* Shape            : X(↔): {psd_chunk.shape[1]}, Y(↕): {psd_chunk.shape[0]}, "
                      f"Freq: {psd_chunk.shape[2]}")
                print(f"=================================================================")
    except RuntimeError as e:
        print("[Warning] Unable to read or parse Metadata (meta.txt).")
        identifier = 'None'
        metadata = {}
    chunk_instance = PSDChunk(identifier, psd_chunk, psd_chunk_freq, metadata)
    return chunk_instance


def rotate_psd_chunk(psd_chunk: np.ndarray,
                     rotate_90d: int
                     ) -> np.ndarray:
    if rotate_90d % 4 != 0:
        return np.ascontiguousarray(np.rot90(psd_chunk, k=rotate_90d, axes=(0, 1)))
    else:
        return psd_chunk


def convert_watt_to_dbm(psd_chunk: np.ndarray,
                        correction: Union[int, float] = 30
                        ) -> np.ndarray:
    return 10 * np.log10(psd_chunk) + correction
