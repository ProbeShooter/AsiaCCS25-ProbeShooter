#!/usr/local/bin/python

import sys
import time
import itertools
import numpy as np
from tqdm import tqdm
from dummy_hardware_api import *


# ===== Parameters ====================================================================================================
# Dataset path
dataset_path = r"/root/ProbeShooter/PSD-chunks/new-psd-chunk-id"

# Rotation
PSD_CHUNK_ROTATE_90d = 0

# Spectrum analyzer
SA_PORT_IP = "192.168.18.121"
SA_FREQ_START = 500e6
SA_FREQ_STOP = 1600e6
SA_FREQ_RBW = 50e3
SA_FREQ_BINS = 40001
SA_TRACE_AVG = 1

# Position (x, y)
POS_LEFT_TOP = (1400000, 500000)  # Origin
POS_RIGHT_BOTTOM = (1600000, 900000)
POS_DOWN_Z = 1600000

# Grid
GRID_X_DIV = 101
GRID_Y_DIV = 101

# XYZ-motorized table
XYZ_SERIAL_PORT = "COM4"
XYZ_MAX_POS_X = int(3e6)
XYZ_MAX_POS_Y = int(3e6)
XYZ_MAX_POS_Z = int(3e7)
XYZ_MAX_VELOCITY = 2047
XYZ_VELOCITY = XYZ_MAX_VELOCITY
# =====================================================================================================================


if __name__ == '__main__':
    print("[ CAUTION ] This script is read-only.\n"
          "  To execute the script, you must connect the API of your device.\n"
          "  Please refer to the source code of this script.")
    exit(-1)


# ===== Equipments ====================================================================================================
    xyz = DummyXYZ()
    xyz.connect(port=XYZ_SERIAL_PORT)
    xyz.set_params(XYZ_MAX_POS_X, XYZ_MAX_POS_Y, XYZ_MAX_POS_Z, XYZ_MAX_VELOCITY)

    sa = DummySpectrumAnalyzer()
    sa.connect(SA_PORT_IP)
    sa.set_params(SA_FREQ_START, SA_FREQ_STOP, SA_FREQ_RBW, SA_FREQ_BINS)
# =====================================================================================================================


# ===== Grid coordinate generation ====================================================================================
    distance_to_dest = (POS_RIGHT_BOTTOM[0] - POS_LEFT_TOP[0], POS_RIGHT_BOTTOM[1] - POS_LEFT_TOP[1])
    assert (GRID_X_DIV % 2 == 1) and (GRID_Y_DIV % 2 == 1)
    x_space = np.linspace(POS_LEFT_TOP[0], POS_LEFT_TOP[0] + distance_to_dest[0], GRID_X_DIV, dtype=np.int32)
    y_space = np.linspace(POS_LEFT_TOP[1], POS_LEFT_TOP[1] + distance_to_dest[1], GRID_Y_DIV, dtype=np.int32)
    xy_space = list((itertools.product(x_space, y_space)))
    xy_space_with_id = [(idx, (idx // GRID_Y_DIV, idx % GRID_Y_DIV), t) for idx, t in enumerate(xy_space)]
    for i in range(GRID_Y_DIV, GRID_Y_DIV ** 2, GRID_Y_DIV * 2):
        temp = xy_space_with_id[i: i + GRID_Y_DIV]
        xy_space_with_id = xy_space_with_id[:i] + temp[::-1] + xy_space_with_id[i + GRID_Y_DIV:]
# =====================================================================================================================


# ===== PSD chunk acquisition =========================================================================================
    # Position initialization
    xyz.move_to_xyz(POS_LEFT_TOP[0], POS_LEFT_TOP[1], POS_DOWN_Z, velocity=XYZ_VELOCITY)

    start_t = time.time()
    data = np.zeros(shape=(GRID_Y_DIV, GRID_X_DIV, SA_FREQ_BINS), dtype=np.float32)
    tqdm_progress = tqdm(range(len(xy_space_with_id)), leave=True, ncols=100, ascii=True, file=sys.stdout)
    for pos_id, (id_x, id_y), (target_x, target_y) in xy_space_with_id:

        # Move to the next position
        xyz.move_to_xyz(int(target_x), int(target_y), None, velocity=XYZ_VELOCITY)

        # Spectrum sweep
        sa.trigger_single_sweep()

        #  PSD / Frequency data receiving
        freq, psd = sa.get_psd() if SA_TRACE_AVG == 1 else sa.get_psd_averaged(SA_TRACE_AVG)
        data[id_y, id_x] = psd

        # Store PSD and metadata
        if pos_id == 0:
            meta = sa.get_status_dict()
            meta['grid_x_div'] = GRID_X_DIV
            meta['grid_y_div'] = GRID_Y_DIV
            meta['pos_left_top'] = POS_LEFT_TOP
            meta['pos_right_bottom'] = POS_RIGHT_BOTTOM
            meta['pos_down_z'] = POS_DOWN_Z
            meta['rot_90d'] = PSD_CHUNK_ROTATE_90d
            with open(dataset_path + f"\\meta.txt", "w") as fp:
                fp.write(str(meta))
            np.save(dataset_path + f"\\freq.npy", freq)

        # tqdm progress update
        tqdm_progress.update(1)
        pass

    tqdm_progress.close()
    end_t = time.time()
    print(f'Scanning completed. ({(end_t - start_t) / 60}m)')
# =====================================================================================================================


# ===== Export PSD and metadata =======================================================================================
    # Export PSD chunk
    if PSD_CHUNK_ROTATE_90d % 4 != 0:
        data = np.ascontiguousarray(np.rot90(data, k=PSD_CHUNK_ROTATE_90d, axes=(0, 1)))
    np.save(dataset_path + f"\\psd_chunk.npy", data)
    
    # Export metadata (overwrite)
    meta['duration_s'] = end_t - start_t
    with open(dataset_path + f"\\meta.txt", "w") as fp:
        fp.write(str(meta))
    print('Export completed...!')
# =====================================================================================================================


# ===== Devices disconnection =========================================================================================
    xyz.disconnect()
    sa.disconnect()
# =====================================================================================================================
