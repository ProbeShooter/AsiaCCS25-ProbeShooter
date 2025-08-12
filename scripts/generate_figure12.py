#!/usr/local/bin/python

import sys
import numpy as np
from probeshooter import *
from matplotlib.font_manager import FontProperties


output_path = r"/root/ProbeShooter/scripts/output"
database_root = r"/root/ProbeShooter/PSD-chunks"
base_path = database_root + r"/PSP-RPI4-dynamic-frequency"
psd_chunk = load_psd_chunk(base_path, rotate_90d=0)
real_freq = np.load(base_path + "/real_freq.npy")
tot_psd_cnt = real_freq.shape[0] * real_freq.shape[1]
gadget_clock = 17


def estimate_core_clock(psd, freq, opp_freq_list, side_band_hz):
    power_density_list = []
    for g_clock in opp_freq_list:
        fc_selector = ((g_clock - side_band_hz) <= freq) & (freq <= (g_clock + side_band_hz))
        power_density_list.append(np.mean(psd[fc_selector]))
        pass
    power_density_list = np.array(power_density_list)
    return opp_freq_list[np.argmax(power_density_list)]


# Known clock
Mclock = np.empty(shape=(101, 101), dtype=np.float32)
M1 = np.empty(shape=(101, 101), dtype=np.float32)
M2 = np.empty(shape=(101, 101), dtype=np.float32)

# Generate pseudo-clock map
clock_by_acc = []
unique_clock = np.unique(real_freq)
for pseudo_acc in [0.25, 0.5, 0.75, 1]:
    manip_freq = np.copy(real_freq)
    pos_candidate = np.random.choice(np.arange(101 * 101), size=round((1 - pseudo_acc) * tot_psd_cnt), replace=False)
    for rand_idx in pos_candidate:
        pos1, pos2 = rand_idx // 101, rand_idx % 101
        original = manip_freq[pos1, pos2]
        while True:
            new = np.random.choice(unique_clock)
            if original != new:
                manip_freq[pos1, pos2] = new
                break
        pass
    clock_by_acc.append(manip_freq)
    pass


leakage_maps = []
acc_maps = []
for clock_selector in clock_by_acc:
    acc_map = np.empty(shape=(101, 101), dtype=np.bool_)
    for pos1 in range(101):
        for pos2 in range(101):
            _psd = psd_chunk.data[pos1, pos2, :]
            _f_clock = real_freq[pos1, pos2]

            estimated_clock = clock_selector[pos1, pos2]

            if estimated_clock == _f_clock:
                acc_map[pos1, pos2] = True
            else:
                acc_map[pos1, pos2] = False

            #########################
            # target_clock = _f_clock
            target_clock = estimated_clock * 1e6
            #########################

            target_freq_hz_list = [target_clock,
                                   target_clock - (target_clock / gadget_clock),
                                   target_clock + (target_clock / gadget_clock)]
            nearset_indices = []
            diff_hz = []
            for t_hz in target_freq_hz_list:
                idx = np.argmin(np.abs(psd_chunk.freq - t_hz))
                nearset_indices.append(idx)
                diff_hz.append(np.abs(t_hz - psd_chunk.freq[idx]))
                pass
            nearset_indices = np.array(nearset_indices, dtype=np.int32)
            diff_hz = np.array(diff_hz, dtype=np.float64)
            if np.sum(nearset_indices == 0) > 0 or np.sum(nearset_indices == len(psd_chunk.freq) - 1) > 0:
                print("[Warning] The frequency of the edge has been selected.", file=sys.stderr)

            Mclock[pos1, pos2] = _psd[nearset_indices[0]]
            M1[pos1, pos2] = _psd[nearset_indices[1]]
            M2[pos1, pos2] = _psd[nearset_indices[2]]
            pass
    leakage_maps.append((M1 + M2) / 2)
    acc_maps.append(acc_map)

target_maps = leakage_maps
target_maps_median_uniform = [simple_2d_filter(m, 'mean', (7, 7)) for m in target_maps]
result_dicts = []
for core_id, m in enumerate(target_maps_median_uniform):
    humps_mask_xy_list = find_top_n_percent_loc_2d(m, 0.9)
    r = aim_points_extraction(combined_leakage_map_2d=m, hump_mask_xy_list=humps_mask_xy_list, top_n=0.05)
    result_dicts.append(r)
    print(f"CORE{core_id}")
    for loc in r['final_pt_xy']:
        real_x_mm, real_y_mm = convert_to_mm_location_from_origin(m, loc, (7.48, 6.64))
        print(f"Real Location from origin: (→{real_x_mm:.4f}mm, ↓{real_y_mm:.4f}mm)", )
    print()


# Figure generation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors


# Setting
f_target_maps = target_maps
label_size = 17
unit = 'nw'
cmap_str = 'nipy_spectral'
only_pt = False
only_area = False
legend = True
marker_size = 100
marker_border_size = 400
legend_font_size: int = 8
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
for i, acc in zip(range(4), [0.25, 0.5, 0.75, 1.0]):
    ax = fig.add_subplot(gs[i])
    im = ax.imshow(f_target_maps[i] * unit_mul[unit], interpolation='none', cmap=cmap_str)
    if i == 0:
        _temp_im = im
    ax.set_title(f'Acc. {int(acc * 100)}%', fontsize=label_size)
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
            ax_xy.legend(prop=font_properties, handletextpad=0.2, loc='upper left')

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

fig.savefig(f"{output_path}/figure12.pdf")
