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
from typing import Union
from sklearn.cluster import DBSCAN


__all__ = [
    'aim_points_extraction'
]


def aim_points_extraction(combined_leakage_map_2d: np.ndarray,
                          hump_mask_xy_list: np.ndarray,
                          top_n: Union[int, float] = 0.05,
                          dbscan_min_samples: int = 5,
                          dbscan_eps: float = 1.5
                          ) -> dict:
    result = {}
    model = DBSCAN(metric='euclidean', min_samples=dbscan_min_samples, eps=dbscan_eps)
    label_pre_c = model.fit_predict(hump_mask_xy_list)
    unique_labels, unique_counts = np.unique(label_pre_c, return_counts=True)
    result['cluster_cnt'] = len(unique_labels)

    all_cluster_loc_xy_list = []
    all_cluster_val_list = []
    all_cluster_top_n_loc_xy_list = []
    all_cluster_top_n_val_list = []
    all_cluster_top_n_filtered_loc_xy_list = []
    all_cluster_top_n_filtered_val_list = []

    for uniq_l in unique_labels:
        if uniq_l == -1:
            continue
        cluster_loc_xy_list = hump_mask_xy_list[label_pre_c == uniq_l]
        cluster_val_list = np.array([combined_leakage_map_2d[y, x] for x, y in cluster_loc_xy_list])

        all_cluster_loc_xy_list.append(cluster_loc_xy_list)
        all_cluster_val_list.append(cluster_val_list)

        sorted_idx = np.argsort(cluster_val_list)[::-1]
        if 0 < top_n < 1:
            _top_n = max(int(len(sorted_idx) * top_n), 5)
        elif 5 <= top_n:
            _top_n = 5
        else:
            assert False, "Invalid 'top_n'"

        all_cluster_top_n_loc_xy_list.append(cluster_loc_xy_list[sorted_idx[:_top_n]])
        all_cluster_top_n_val_list.append(cluster_val_list[sorted_idx[:_top_n]])

    for xy_list, val_list in zip(all_cluster_top_n_loc_xy_list, all_cluster_top_n_val_list):
        m = DBSCAN(metric='euclidean', min_samples=dbscan_min_samples, eps=dbscan_eps)
        label_pre_c = m.fit_predict(xy_list)
        unique_labels, unique_counts = np.unique(label_pre_c, return_counts=True)
        if len(unique_labels) != 1:
            max_idx = np.argmax(unique_counts)
            max_label = unique_labels[max_idx]
            all_cluster_top_n_filtered_loc_xy_list.append(xy_list[label_pre_c == max_label])
            all_cluster_top_n_filtered_val_list.append(val_list[label_pre_c == max_label])
        else:
            all_cluster_top_n_filtered_loc_xy_list.append(xy_list)
            all_cluster_top_n_filtered_val_list.append(val_list)
        pass

    all_cluster_val_sum = np.array([np.mean(i) for i in all_cluster_top_n_filtered_val_list])
    all_cluster_confidence = all_cluster_val_sum / np.sum(all_cluster_val_sum)
    final_sorted_idx = all_cluster_confidence.argsort()[::-1]

    result['each_cluster_confidence'] = all_cluster_confidence[final_sorted_idx]
    result['each_cluster_pt_xy'] = []
    result['each_cluster_pt_val'] = []
    result['each_cluster_top_n_pt_xy'] = []
    result['each_cluster_top_n_pt_val'] = []
    result['each_cluster_top_n_pt_xy_filtered'] = []
    result['each_cluster_top_n_pt_val_filtered'] = []

    for idx in final_sorted_idx:
        result['each_cluster_pt_xy'].append(all_cluster_loc_xy_list[idx])
        result['each_cluster_pt_val'].append(all_cluster_val_list[idx])
        result['each_cluster_top_n_pt_xy'].append(all_cluster_top_n_loc_xy_list[idx])
        result['each_cluster_top_n_pt_val'].append(all_cluster_top_n_val_list[idx])
        result['each_cluster_top_n_pt_xy_filtered'].append(all_cluster_top_n_filtered_loc_xy_list[idx])
        result['each_cluster_top_n_pt_val_filtered'].append(all_cluster_top_n_filtered_val_list[idx])
        pass

    result['final_pt_xy'] = [np.mean(pos, axis=0) for pos in result['each_cluster_top_n_pt_xy_filtered']]
    return result
