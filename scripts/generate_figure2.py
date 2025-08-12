#!/usr/local/bin/python

from probeshooter import *


output_path = r"/root/ProbeShooter/scripts/output"
database_root = r"/root/ProbeShooter/PSD-chunks"
base_path = database_root + r"/PSA-IMXRT1061-24mhz"
psd_chunk = load_psd_chunk(base_path, rotate_90d=0)


f_target = 23.5035e6
p_slice_target = psd_chunk.parse_from_nearest_freq_list([f_target])
m_target = p_slice_target.data[:, :, 0]
fig = visualize_single_map_with_2d_arr(m_target, unit='pw')

fig.savefig(f"{output_path}/figure2(d).pdf")
