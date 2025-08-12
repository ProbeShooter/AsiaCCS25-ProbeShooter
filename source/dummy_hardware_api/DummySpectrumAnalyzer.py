import numpy as np


__all__ = [
    'DummySpectrumAnalyzer'
]


class DummySpectrumAnalyzer:
    def connect(self, ip_addr) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def trigger_single_sweep(self) -> None:
        pass

    def get_psd(self) -> (np.ndarray, np.ndarray):
        freq, psd = None, None
        return freq, psd

    def get_psd_averaged(self, avg_number) -> (np.ndarray, np.ndarray):
        freq, psd = None, None
        return freq, psd

    def set_params(self, freq_start, freq_stop, freq_rbw, freq_bins) -> None:
        pass

    def get_status_dict(self) -> dict:
        status_dict = {}
        return status_dict
    pass
