import holoviews as hv
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft
import scipy.signal
import xarray as xr


class RingdownAnalysis:
    def __init__(self, data, init_data=None):
        """
        data: micromagneticdata from Ubermag simulations
        init_data: initial field data.
        """
        self.data = data
        self.init_data = init_data
        self.time_values = self.data.table.data["t"].values

        self.diff_xarr = None
        self.freq = None
        self.power_spa = None
        self.power_ave = None
        self.power_phase = None
        self.peaks = None

    def select_subregion(self, subregion="both"):
        """
        Dynamically selects the field orientation for a given subregion
        and stores the result.
        subregion: The subregion to process (e.g., 'both', 'bottom', 'top', etc.).
        """
        if subregion == "both" or subregion is None:
            init_field_subregion = self.init_data[-1].orientation.to_xarray()
            time_drive = self.data.register_callback(lambda field: field.orientation)
        else:
            init_field_subregion = self.init_data[-1][subregion].orientation.to_xarray()
            time_drive = self.data.register_callback(
                lambda field: field[subregion].orientation
            )
        time_drive_xarr = time_drive.to_xarray()
        self.diff_xarr = time_drive_xarr - init_field_subregion

    def fft_analysis1(self, subregion="both"):
        """
        FFT analysis on the system or a specific subregion and stores the results.
        subregion: The subregion to process (e.g., 'both', 'bottom', 'top', etc.).
        """
        self.select_subregion(subregion)
        self.freq = np.fft.rfftfreq(
            self.diff_xarr.values.shape[0], d=self.diff_xarr["t"].values[0]
        )
        fft_np = np.fft.rfft(self.diff_xarr.values, axis=0, norm="ortho")
        fft = xr.DataArray(
            fft_np,
            coords={
                "freq_t": self.freq,
                "x": self.diff_xarr["x"],
                "y": self.diff_xarr["y"],
                "z": self.diff_xarr["z"],
                "vdims": self.diff_xarr["vdims"],
            },
            dims=["freq_t", "x", "y", "z", "vdims"],
        )

        self.power_spa = np.abs(fft) ** 2
        self.power_phase = np.arctan2(fft.imag, fft.real)
        self.power_ave = self.power_spa.mean(axis=(1, 2, 3))

    def fft_analysis(self):
        """
        Performs FFT analysis on the system, converts the data into xarray.
        returns power_spa, power_phase and power_ave in np.arrays
        Stores the results in the instance variables.
        """
        init_field = self.init_data
        time_drive = self.data.register_callback(lambda field: field.orientation)
        time_drive_xarr = time_drive.to_xarray()
        self.diff_xarr = time_drive_xarr - init_field[-1].orientation.to_xarray()
        self.freq = np.fft.rfftfreq(
            self.diff_xarr.values.shape[0], d=self.diff_xarr["t"].values[0]
        )
        fft_np = np.fft.rfft(self.diff_xarr.values, axis=0, norm="ortho")
        fft = xr.DataArray(
            fft_np,
            coords={
                "freq_t": self.freq,
                "x": self.diff_xarr["x"],
                "y": self.diff_xarr["y"],
                "z": self.diff_xarr["z"],
                "vdims": self.diff_xarr["vdims"],
            },
            dims=["freq_t", "x", "y", "z", "vdims"],
        )

        self.power_spa = np.abs(fft) ** 2
        self.power_phase = np.arctan2(fft.imag, fft.real)
        self.power_ave = self.power_spa.mean(axis=(1, 2, 3))

    def find_peaks(self, prominence=1e-5, axis=0):
        """
        Finds the peaks in a selected 1D slice of the power spectral density (PSD).

        prominence: Prominence of the peaks.
        axis: The axis or index to select a 1D slice of the power_ave
        array for peak detection.
        return: Indices of the peaks and their corresponding frequency values.
        """
        if self.power_ave is None or self.freq is None:
            raise ValueError(
                "FFT analysis not performed yet. Run fft_analysis() first."
            )
        if len(self.power_ave.shape) > 1:
            power_ave_1d = self.power_ave.isel(vdims=axis)
        else:
            power_ave_1d = self.power_ave
        peaks, _ = scipy.signal.find_peaks(power_ave_1d, prominence=prominence)
        self.peaks = peaks

    def plot_peaks(self):
        """
        Plots the amplitude, phase and overlay at the frequencies corresponding
        to detected peaks.
        """
        if self.peaks is None:
            raise ValueError("No peaks detected. Run find_peaks() first.")

        if self.power_spa is None or self.power_phase is None or self.freq is None:
            raise ValueError(
                "FFT analysis not performed yet. Run fft_analysis() first."
            )

        for peak_freq_idx in self.peaks:
            frequency_value = self.freq[peak_freq_idx]
            power_spa_at_freq_idx = self.power_spa[peak_freq_idx]
            phase_at_freq_idx = self.power_phase[peak_freq_idx]

            fig, axs = plt.subplots(3, 3, figsize=(15, 10))
            for i, ax in enumerate(axs[0, :]):
                amplitude_data = power_spa_at_freq_idx[:, :, 0, i]
                im = ax.imshow(
                    amplitude_data.T, cmap="coolwarm", aspect="equal", origin="lower"
                )
                ax.set_title(
                    f'{["mx", "my", "mz"][i]} '
                    f'Amplitude at {frequency_value/1e9:.2f} GHz'
                )
                ax.set_xticks([])
                ax.set_yticks([])
                plt.colorbar(im, ax=ax)
            for i, ax in enumerate(axs[1, :]):
                phase_data = phase_at_freq_idx[:, :, 0, i]
                im = ax.imshow(
                    phase_data.T, cmap="twilight", aspect="equal", origin="lower"
                )
                ax.set_title(
                    f'{["mx", "my", "mz"][i]} Phase at {frequency_value/1e9:.2f} GHz'
                )
                ax.set_xticks([])
                ax.set_yticks([])
                plt.colorbar(im, ax=ax)
            for i, ax in enumerate(axs[2, :]):
                phase_data = phase_at_freq_idx[:, :, 0, i]
                amplitude_data = power_spa_at_freq_idx[:, :, 0, i]
                im = ax.imshow(
                    phase_data.T,
                    cmap="hsv",
                    aspect="equal",
                    origin="lower",
                    alpha=amplitude_data.T / amplitude_data.T.max(),
                )
                ax.set_title(
                    f'{["mx", "my", "mz"][i]} Phase (alpha)'
                    f' at {frequency_value/1e9:.2f} GHz'
                )
                ax.set_xticks([])
                ax.set_yticks([])
                plt.colorbar(im, ax=ax)

            plt.tight_layout()
            plt.show()

    def inverse_fft(self, peak_index=-1, width=0.001, factor=1):
        """
        inverse FFT for a selected frequency range based on the specified peak.
        peak_index: Index of the frequency peak, default is last index
        width: The width around the peak to include in the frequency range.
        scale_factor: The scaling factor to apply when creating the mode_xr DataArray.
        """
        if self.peaks is None or self.freq is None:
            raise ValueError(
                "No peaks detected or FFT analysis not performed. "
                "Run fft_analysis() and find_peaks() first."
            )
        freq_of_interest = self.freq[self.peaks]
        first_peak = freq_of_interest[peak_index]
        lower_bound = first_peak - width
        upper_bound = first_peak + width

        fft_mode = np.zeros_like(self.power_spa)
        for i in range(len(self.freq)):
            if lower_bound <= self.freq[i] <= upper_bound:
                fft_mode[i] = self.power_spa[i]

        mode = np.fft.irfft(fft_mode, axis=0)
        scale_factor = 1 / mode.max() * factor

        init_field = self.init_data[-1].orientation.array
        mode_xr = xr.DataArray(
            scale_factor * mode + init_field,
            coords={
                "t": self.diff_xarr["t"].values,
                "x": self.diff_xarr["x"],
                "y": self.diff_xarr["y"],
                "z": self.diff_xarr["z"],
                "vdims": self.diff_xarr["vdims"],
            },
            dims=["t", "x", "y", "z", "vdims"],
            name="mode_xr",
        )

        hv.extension("bokeh")
        img = hv.Dataset(mode_xr.sel(vdims="z")).to(
            hv.Image, kdims=["x", "y"], dynamic=True
        )
        img.opts(
            colorbar=True,
            cmap="coolwarm",
            frame_width=500,
            aspect="equal",
            clim=(-1, 1),
        )
        return img

    def extract_mz_subregion(self, subregion="both"):
        """
        Extracts the mean magnetisation along the z-axis for a given
        subregion or whole system.

        subregion: The subregion to process (e.g., 'both', 'bottom', 'top', etc.).
        return: An array of mz for the subregion.
        """

        def extract_mz(field):
            return (
                field.orientation.mean()[2]
                if subregion == "both"
                else field[subregion].orientation.mean()[2]
            )

        mz_values = np.array(
            [extract_mz(self.data[i]) for i in range(len(self.time_values))]
        )
        return mz_values

    def spatially_averaged_psd(self, subregion="both"):
        """
        Calculates the spatially averaged PSD using FFT for the whole
        system or a subregion.

        subregion: The subregion to process (e.g., 'whole', 'bottom', 'top', etc.).
        return: A tuple of (frequency, magnitude) for the PSD.
        """
        mz_values = self.extract_mz_subregion(subregion=subregion)
        sample_spacing = self.time_values[1] - self.time_values[0]
        magnitude = np.abs(scipy.fft.rfft(mz_values) ** 2)
        frequency = scipy.fft.rfftfreq(len(mz_values), sample_spacing)
        return frequency, magnitude

    def plot_magnetisation(self, subregions, xlabel="t (nm)", ylabel="<mz>"):
        """
        Plots the magnetisation values for multiple subregions.

        subregions: A list of subregion names to plot.
        title: The title of the plot.
        xlabel: The label for the x-axis.
        ylabel: The label for the y-axis.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for subregion in subregions:
            mz_values = self.extract_mz_subregion(subregion)
            ax.plot(self.time_values / 1e9, mz_values, label=subregion)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        plt.show()
