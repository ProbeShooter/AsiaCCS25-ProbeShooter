#!/usr/local/bin/python

from probeshooter import *
import glob

output_path = r"/root/ProbeShooter/scripts/output"
database_root = r"/root/ProbeShooter/PSD-chunks"
target_dir = glob.glob(f"{database_root}/PSA-RPI4-multi-core-each-1200mhz/*")

# Leakage combination
target_maps = []
for core_id, psd_chunk_dir in enumerate(target_dir):
    center = 1210.0115e6
    sub_span = 5e3
    psd_chunk = load_psd_chunk(psd_chunk_dir, rotate_90d=0)
    p_slice_target = psd_chunk.parse_from_freq_range_closed(center - sub_span, center + sub_span)
    m_target = p_slice_target.data.sum(axis=2)
    target_maps.append(m_target)

# Median filter
target_maps_median = [simple_2d_filter(m, 'median', (3, 3)) for m in target_maps]

# Uniform filter
target_maps_median_uniform = [simple_2d_filter(m, 'mean', (5, 5)) for m in target_maps_median]

# Aiming
result_dicts = []
for core_id, m in enumerate(target_maps_median_uniform):
    if core_id == 3:
        humps_mask_xy_list = find_top_n_percent_loc_2d(m, 0.81)
        r = aim_points_extraction(combined_leakage_map_2d=m, hump_mask_xy_list=humps_mask_xy_list, top_n=0.03)
    else:
        humps_mask_xy_list = find_top_n_percent_loc_2d(m, 0.75)
        r = aim_points_extraction(combined_leakage_map_2d=m, hump_mask_xy_list=humps_mask_xy_list, top_n=0.03)
    result_dicts.append(r)
    print(f"CORE{core_id}")
    for loc in r['final_pt_xy']:
        real_x_mm, real_y_mm = convert_to_mm_location_from_origin(m, loc, (7.48, 6.64))
        print(f"Real Location from origin: (→{real_x_mm:.4f}mm, ↓{real_y_mm:.4f}mm)", )
    print()
    pass


# Figure generation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties


# Setting
f_target_maps = target_maps
label_size = 17
unit = 'pw'
cmap_str = 'nipy_spectral'
only_pt = False
only_area = False
legend = True
marker_size = 100
marker_border_size = 400
legend_font_size: int = 7
chip_margin = 0
legend_loc_bbox_to_anchor = None

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['mathtext.fontset'] = 'dejavuserif'

unit_map = {'w': 'W', 'uw': r'$\mu$W', 'nw': 'nW', 'pw': 'pW', 'dbm': 'dBm', None: ''}
unit_mul = {'w': 1, 'uw': 1e6, 'nw': 1e9, 'pw': 1e12, 'dbm': 1, None: 1}


fig = plt.figure(figsize=(9.5, 5))
gs = GridSpec(2, 4, wspace=0.09, hspace=-0.10,
              left=0.08, right=1.10, bottom=0.09, top=0.97)

axes_top = []
axes_bot = []

# 0 ~ 4
_temp_im = None
for i in range(4):
    ax = fig.add_subplot(gs[i])
    im = ax.imshow(f_target_maps[i] * unit_mul[unit], interpolation='none', cmap=cmap_str)
    if i == 0:
        _temp_im = im
    ax.set_title(f'Core{i}', fontsize=label_size)
    axes_top.append(ax)

# 5 ~ 8
for i in range(4, 8):
    ax_xy = fig.add_subplot(gs[i])
    cmap = plt.get_cmap('Set1').colors

    result_dict = result_dicts[i - 4]
    reference_2d_arr = f_target_maps[0]
    if not only_pt:
        bm = np.full_like(reference_2d_arr, dtype=np.float32, fill_value=0)
        for xy_list_1, xy_list_2, xy_list_3 in zip(result_dict['each_cluster_pt_xy'],
                                                   result_dict['each_cluster_top_n_pt_xy'],
                                                   result_dict['each_cluster_top_n_pt_xy_filtered']):
            for x, y in xy_list_1:
                bm[y, x] = 0.1
            for x, y in xy_list_2:
                bm[y, x] = 0.3
            for x, y in xy_list_3:
                bm[y, x] = 0.8
            pass
        ax_img = ax_xy.imshow(bm, cmap='binary', vmin=0, vmax=1)
    else:
        ax_img = ax_xy.imshow(np.zeros_like(reference_2d_arr), cmap='binary', vmin=0, vmax=1)

    if not only_area:
        for pri, ((x, y), c, conf) in enumerate(zip(result_dict['final_pt_xy'], cmap,
                                                    result_dict['each_cluster_confidence']), 1):
            h1 = ax_xy.vlines([x], ymin=-0.5 - chip_margin - 1, ymax=reference_2d_arr.shape[0] + chip_margin + 1,
                              linestyles='--', linewidth=0.5, color=c, alpha=0.8)
            h2 = ax_xy.hlines([y], xmin=-0.5 - chip_margin - 1, xmax=reference_2d_arr.shape[1] + chip_margin + 1,
                              linestyles='--', linewidth=0.5, color=c, alpha=0.8)
            sc = ax_xy.scatter(x, y, marker='x', label=f'({pri}) conf.={conf:0.3f}', color=c, s=marker_size)
            sc_border = ax_xy.scatter(x, y, facecolors='none', edgecolors=c, s=marker_border_size, marker='o',
                                      alpha=0.7)
            h1.set_zorder(1)
            h2.set_zorder(1)
            sc_border.set_zorder(2)
            sc.set_zorder(3)

    if legend:
        if not only_pt and only_area:
            cmap = plt.get_cmap('binary')
            ax_xy.scatter(-1000, -1000, s=100, marker='s', label='Type1', color=cmap(0.1))
            ax_xy.scatter(-1000, -1000, s=100, marker='s', label='Type2', color=cmap(0.3))
            ax_xy.scatter(-1000, -1000, s=100, marker='s', label='Type3', color=cmap(0.8))
        font_properties = FontProperties(size=legend_font_size)
        if legend_loc_bbox_to_anchor is not None:
            ax_xy.legend(prop=font_properties, handletextpad=0.2, bbox_to_anchor=legend_loc_bbox_to_anchor)
        else:
            if i - 4 == 0:
                ax_xy.legend(prop=font_properties, handletextpad=0.2, loc='upper right')
            if i - 4 == 1:
                ax_xy.legend(prop=font_properties, handletextpad=0.2, loc='upper right')
            if i - 4 == 2:
                ax_xy.legend(prop=font_properties, handletextpad=0.2, loc='lower left')
            if i - 4 == 3:
                ax_xy.legend(prop=FontProperties(size=6), handletextpad=0.2, loc='lower right')

    ax_xy.set_xlim((-0.5, reference_2d_arr.shape[1]))
    ax_xy.set_ylim((reference_2d_arr.shape[0], -0.5))

    axes_bot.append(ax_xy)

# Label remove
for i, ax in enumerate(axes_top + axes_bot):
    if i % 4 != 0:
        ax.set_yticks([])
    if i < 4:
        ax.set_xticks([])
    else:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
        ax.tick_params(axis='x', labelrotation=45)
    pass

cbar = fig.colorbar(_temp_im, ax=axes_top, shrink=0.81, location='right', pad=0.01, spacing='proportional')
cbar.ax.set_title(f"[{unit_map[unit]}]", fontsize=10)
_cbar = fig.colorbar(ax_img, ax=axes_bot, shrink=0.9, location='right', pad=0.01)
_cbar.ax.set_visible(False)

fig.text(0.02, 0.5, 'X-offset [pts]', va='center', rotation='vertical', fontsize=label_size, ha='center')
fig.text(0.5, 0.025, 'Y-offset [pts]', ha='center', fontsize=label_size, va='center')

fig.savefig(f"{output_path}/figure20(a).pdf")
