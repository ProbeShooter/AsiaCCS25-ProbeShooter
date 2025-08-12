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

import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from typing import Optional, Union, Tuple


__all__ = [
    'visualize_single_map_with_2d_arr',
]


def visualize_single_map_with_2d_arr(arr_2d: np.ndarray,
                                     fig_title: Optional[str] = None,
                                     interpolation: str = 'none',
                                     cmap='nipy_spectral',
                                     unit: Optional[str] = None,
                                     fig_size: Optional[Tuple[float, float]] = None,
                                     patch_xy_list: Optional[Union[list, np.ndarray]] = None,
                                     histogram: bool = False,
                                     show: bool = True
                                     ) -> plt.Figure:
    assert len(arr_2d.shape) == 2
    if histogram:
        gs = GridSpec(nrows=1, ncols=5, width_ratios=[10, 0.2, 0.6, 1.5, 1.2], wspace=0)
        if fig_size is None:
            fig_size = (5.7, 4)
    else:
        gs = GridSpec(nrows=1, ncols=3, width_ratios=[10, 0.1, 0.6], wspace=0)
        if fig_size is None:
            fig_size = (3.8, 3)
    fig: plt.Figure = plt.figure(figsize=fig_size)
    fig.canvas.manager.set_window_title(f"Single Map - {str(datetime.datetime.now())}")
    ax_xy: plt.Axes = fig.add_subplot(gs[0, 0])
    ax_cbar: plt.Axes = fig.add_subplot(gs[0, 2])
    _draw_single_map(fig=fig,
                     ax_xy=ax_xy,
                     ax_cbar=ax_cbar,
                     psd_chunk=arr_2d[:, :, np.newaxis],
                     die_margin_pts_xy=None,
                     title=fig_title,
                     enable_mm_notation=False,
                     mm_notation_xy=None,
                     mm_notation_div=None,
                     interpolation=interpolation,
                     cmap=cmap,
                     unit=unit)

    # Histogram
    if histogram:
        ax_histogram = fig.add_subplot(gs[0, 4])
        ax_histogram.hist(arr_2d.flatten(), bins=50, density=True, orientation='horizontal', color='black')
        ax_histogram.yaxis.set_ticks_position('right')
        ax_histogram.yaxis.set_label_position('right')
        ax_histogram.set_ylim((0, np.max(arr_2d)))
        ax_histogram.set_xticks([])
        ax_histogram.set_yticks([])
        plt.setp(ax_histogram.get_yticklabels(), visible=False)
        plt.setp(ax_histogram.get_yticklabels(), visible=False)
        pass

    if patch_xy_list is not None:
        for x, y in patch_xy_list:
            ax_xy.add_patch(patches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                              lw=1, edgecolor='white', facecolor='white', alpha=0.2))
            ax_xy.add_patch(patches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                              lw=1, edgecolor='white', facecolor='none', alpha=0.8))
        pass

    fig.tight_layout()
    if show:
        fig.show()
    return fig


def _draw_single_map(fig, ax_xy, ax_cbar,
                     psd_chunk: np.ndarray,
                     die_margin_pts_xy: Optional[tuple[int, int]] = None,
                     title: Optional[str] = None,
                     enable_mm_notation: bool = False,
                     mm_notation_xy: Optional[tuple[Union[float, int], Union[float, int]]] = None,
                     mm_notation_div: Optional[int] = None,
                     interpolation: str = 'none',
                     cmap='nipy_spectral',
                     unit: Optional[str] = None
                     ) -> None:
    assert unit in ['w', 'uw', 'nw', 'pw', 'dbm', None]
    unit_map = {'w': 'W', 'uw': r'$\mu$W', 'nw': 'nW', 'pw': 'pW', 'dbm': 'dBm', None: ''}
    unit_mul = {'w': 1, 'uw': 1e6, 'nw': 1e9, 'pw': 1e12, 'dbm': 1, None: 1}

    if die_margin_pts_xy is not None:
        if die_margin_pts_xy[0] == 0 and die_margin_pts_xy[1] == 0:
            target_psd_chunk = psd_chunk
        else:
            die_margin_x = die_margin_pts_xy[0]
            die_margin_y = die_margin_pts_xy[1]
            target_psd_chunk = psd_chunk[die_margin_y:die_margin_y * -1, die_margin_x:die_margin_x * -1, :]
    else:
        target_psd_chunk = psd_chunk

    ax_img = ax_xy.imshow(target_psd_chunk.mean(axis=2) * unit_mul[unit],
                          interpolation=interpolation, cmap=cmap, aspect=1)

    fig.colorbar(ax_img, cmap=cmap, cax=ax_cbar, spacing='proportional')
    if title is not None:
        ax_xy.set_title(title)
    if unit is not None:
        ax_cbar.set_xlabel(f"{unit_map[unit]}")

    if enable_mm_notation:
        assert mm_notation_xy is not None and mm_notation_div is not None
        axis_mm_x = mm_notation_xy[0]
        axis_mm_y = mm_notation_xy[1]
        ax_xy.set_xticks(np.linspace(0, target_psd_chunk.shape[1] - 1, mm_notation_div + 1, dtype=np.int32))
        ax_xy.set_xticklabels([f'{i:.02f}' for i in np.linspace(0, axis_mm_x, mm_notation_div + 1, dtype=np.float32)])
        ax_xy.set_yticks(np.linspace(0, target_psd_chunk.shape[0] - 1, mm_notation_div + 1, dtype=np.int32))
        ax_xy.set_yticklabels([f'{i:.02f}' for i in np.linspace(0, axis_mm_y, mm_notation_div + 1, dtype=np.float32)])
        ax_xy.set_xlabel(f"X-offset [mm] (bins: {target_psd_chunk.shape[1]})")
        ax_xy.set_ylabel(f"Y-offset [mm] (bins: {target_psd_chunk.shape[0]})")
    else:
        ax_xy.set_xlabel("X-offset [pts]")
        ax_xy.set_ylabel("Y-offset [pts]")
    pass
