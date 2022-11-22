"""
Respiration Analysis Part 1

This code will take EEG data, extract the relevant respiration data from
three times for 100 seconds (during the BCT, right after a cue, and right
before a cue). It will take the average of these rates, and average all
of the respiration rates per subject. It will export the RRV files and
signal tables to the results folder.
"""

export_directory = '../results'


# # IMPORT PACKAGES

import numpy as np
import mne
import matplotlib.pyplot as plt
from mne.filter import filter_data
import scipy
from scipy.signal import find_peaks
import neurokit2 as nk
import pandas as pd
import os

cwd = '/Users/norahwolk/Desktop/bct_tmr/data'
files = os.listdir(cwd)
subs = []
for file in files:
    if file.startswith('sub')==True:
        subs.append(file)

# Turn on interactive plotting
plt.ion()

# # LOAD AND PROCESS DATA

for sub in subs:
    sub_str = sub[:7]

    # Load data
    file_name = os.path.join(cwd,sub)
    raw = mne.io.read_raw_cnt(file_name, preload=True, verbose=False)

    # Apply a bandpass filter from 0.1 to 40 Hz
    raw.filter(0.1, 40)

    events, code_map = mne.events_from_annotations(raw)

    # Get timestamp of when BCT starts (in number of samples).
    bct_start = events[np.where(events[:,2]==23), 0][0][0]
    # Get middle of BCT by adding 5 minutes to the number of samples.
    bct_middle = bct_start + 60*5*raw.info["sfreq"]
    # Convert time of middle of BCT to seconds
    bct_middle = bct_middle / raw.info["sfreq"]

    # Get 100 seconds before and after the cue
    cue_code1 = code_map["227"]
    if "228" in code_map:
        cue_code2 = code_map["228"]
        starting_points = events[np.where(np.isin(events[:,2], [cue_code1, cue_code2])), 0][0][1:]
    else:
        starting_points = events[np.where(events[:,2]==cue_code1), 0][0][1:]

    count=0
    for cue_start in starting_points:
        export_fname_1 = f"{export_directory}/signal_table_{sub_str}_{count}.csv"
        export_fname_2 = f"{export_directory}/rrv_table_{sub_str}_{count}.csv"

        print(sub_str, cue_start, count)
        # cue_start = events[np.where(events[:,2]==22), 0][0][-1]
        uncued_start = cue_start - 100*raw.info["sfreq"]
        uncued_start = uncued_start / raw.info["sfreq"]
        cue_start2 = cue_start / raw.info["sfreq"]

        bct_segment = raw.get_data(picks="RESP", tmin=bct_middle, tmax=bct_middle + 100)
        cue_segment = raw.get_data(picks="RESP", tmin=cue_start2, tmax=cue_start2 + 100)
        control_segment = raw.get_data(picks="RESP", tmin=uncued_start, tmax=uncued_start + 100)

        # Index one column out
        bct_segment = bct_segment[0, :]
        cue_segment = cue_segment[0, :]
        uncued_segment = control_segment[0, :]

        # plot respiration signals

        signals_bct, info_bct= nk.rsp_process(bct_segment, sampling_rate=raw.info["sfreq"])
        nk.rsp_plot(signals_bct)
        plt.suptitle("BCT Respiration Signal")
        plt.close()

        signals_cue, info_cue = nk.rsp_process(cue_segment, sampling_rate=raw.info["sfreq"])
        nk.rsp_plot(signals_cue)
        plt.suptitle("Cue Respiration Signal")
        plt.close()

        signals_uncued, info_uncued = nk.rsp_process(uncued_segment, sampling_rate=raw.info["sfreq"])
        nk.rsp_plot(signals_uncued)
        plt.suptitle("Uncued Respiration Signal")
        plt.close()

        # create table for all 3 conditions with averages of signals
        signal_table = pd.concat([signals_bct.mean(), signals_cue.mean(), signals_uncued.mean()], axis=1)
        signal_table.columns = ["bct", "cue", "uncued"]
        print(signal_table)

        # power spectral density and poincaré plot
        rrv_bct = nk.rsp_rrv(bct_segment, info_bct, sampling_rate=100, show=False)

        rrv_cue = nk.rsp_rrv(cue_segment, info_cue, sampling_rate=100, show=False)

        rrv_uncued = nk.rsp_rrv(uncued_segment, info_uncued, sampling_rate=100, show=False)

        rrv_table = pd.concat([rrv_bct.mean(), rrv_cue.mean(), rrv_uncued.mean()], axis=1)
        rrv_table.columns = ["bct", "cue", "uncued"]
        print(rrv_table)

        signal_table.to_csv(export_fname_1, index_label="measure")
        rrv_table.to_csv(export_fname_2, index_label="measure")

        count=count+1
