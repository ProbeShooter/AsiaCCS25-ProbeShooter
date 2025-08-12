#!/usr/local/bin/python

from probeshooter import *


output_path = r"/root/ProbeShooter/scripts/output"
database_root = r"/root/ProbeShooter/PSD-chunks"
base_path = database_root + r"/PSP-IMXRT1061-24mhz"
psd_chunk = load_psd_chunk(base_path, rotate_90d=0)


f_clock = 24e6
c_gadget = 7

p_slice_clock = psd_chunk.parse_from_nearest_freq_list([f_clock])
p_slice_imd_1 = psd_chunk.parse_from_nearest_freq_list([f_clock + (f_clock / c_gadget)])
p_slice_imd_2 = psd_chunk.parse_from_nearest_freq_list([f_clock - (f_clock / c_gadget)])

m_clock = p_slice_clock.data[:, :, 0]
m_imd_1 = p_slice_imd_1.data[:, :, 0]
m_imd_2 = p_slice_imd_2.data[:, :, 0]
m_imd_mean = (m_imd_1 + m_imd_2) / 2

die_margin_xy = (int(((101 - 1) / 12) * ((12 - 3.75) / 2)),
                 int(((101 - 1) / 12) * ((12 - 3.58) / 2)))

die_map = m_imd_mean[die_margin_xy[1]:die_margin_xy[1] * -1, die_margin_xy[0]:die_margin_xy[0] * -1]
aspect = die_map.shape[1] / die_map.shape[0]

fig_chip = visualize_single_map_with_2d_arr(m_imd_mean, unit='pw', show=False)
fig_die = visualize_single_map_with_2d_arr(die_map, unit='pw', show=False)

fig_chip.savefig(f"{output_path}/figure1(a).pdf")
fig_die.savefig(f"{output_path}/figure1(c).pdf")
