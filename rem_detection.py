"""
This code takes EEG data and detects rapid eye movements. It uses the
hypnogram data CSV file from my sleep_staging_script and currently detects
REMs only during stage R sleep. It will plot two types of graphs, one with
just the raw EOG data, and one with the eye movements highlighted. There
will be three graphs with REMs highlighted, one during wake, one during a
lucid dream, and one during REM sleep.

"""

# # START COMMAND-LINE PARSING

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--subject")
args = parser.parse_args()
print(args.subject)

# # CREATE VARIABLES

subject = args.subject

raw_eeg_data = f'../data/sub-{subject}_ses-001_eeg.cnt'
hypnogram_csv = f'../results/{subject}hypnogram_data.csv'
# eog_full_plot = f'../results/eog_plot.png'
export_directory = '../results'

# # IMPORT PACKAGES

import yasa
import numpy as np
import seaborn as sns
import pandas as pd
import mne
import matplotlib.pyplot as plt
from mne.filter import filter_data
sns.set(font_scale=1.2)
from yasa import rem_detect

# Turn on interactive plotting
plt.ion()

# # LOAD AND PROCESS DATA

# Load data
raw = mne.io.read_raw_cnt(raw_eeg_data, preload=True, verbose=False)

# Apply a bandpass filter from 0.1 to 40 Hz
raw.filter(0.1, 40)

# Change units to uV, name sampling frequency and channel names
data, sf, chan = raw.get_data(units="uV"), raw.info['sfreq'], raw.ch_names

# Specify which channels we will use (L-VEOG, R-HEOG, and EMG)
# (L-VEOG, R-HEOG, and EMG are 3, 4, 5 on the list of channels)
loc = data[3]
roc = data[4]
emg = data[5]

# Import CSV file of hypnogram data from staging code and change it to a list
hypno = pd.read_csv(hypnogram_csv)
stage_hypno = hypno["Stage"].tolist()

# Change the data from a string to integers
int_hypno = yasa.hypno_str_to_int(stage_hypno)
int_hypno = yasa.hypno_upsample_to_data(int_hypno, 1/30, loc, sf)

# Detect rapid eye movements
rem = rem_detect(loc, roc, sf, hypno = int_hypno, include=4)

if rem is None:

    print("No REM found. Not making a plot.")

else:

    # Define sampling frequency and time vector
    times = np.arange(loc.size) / sf

    # # PLOT THE EOG DATA

    # # Plot the signal
    # fig, ax = plt.subplots(1, 1, figsize=(16, 4))
    # plt.plot(times, loc, label='LOC', lw=1.5)
    # plt.plot(times, roc, label='ROC', lw=1.5)
    # plt.plot(times, emg, label='EMG', lw=1.5)
    # plt.xlabel('Time (seconds)')
    # plt.ylabel('Amplitude (uV)')
    # plt.xlim([times.min(), times.max()])
    # plt.title('REM sleep EOG data')
    # plt.legend(loc='best', frameon=False)
    # sns.despine()

    # plt.savefig(eog_full_plot, bbox_inches='tight',dpi=600)
    # plt.close()

    # Get the detection dataframe
    events = rem.summary()
    events.round(3)

    # # PLOT THE DETECTED RAPID EYE MOVEMENTS

    # Get a boolean mask of the rapid eye movements in data
    mask = rem.get_mask()

    loc_highlight = loc * mask[0, :]
    roc_highlight = roc * mask[1, :]

    loc_highlight[loc_highlight == 0] = np.nan
    roc_highlight[roc_highlight == 0] = np.nan

    # Create a dictionary for times that correspond with the events
    plot_cutoffs = {
        "wake": (2182, 2192),
        "lucid": (6455, 6465),
        "rem": (5992, 6002),
    }

    # Create a for loop that will plot one graph per event
    for event_name in ["wake", "lucid", "rem"]:

        # Pull out information from dictionary in seconds
        start_seconds = plot_cutoffs[event_name][0]
        end_seconds = plot_cutoffs[event_name][1]

        # Change to integer and change to sampling frequency
        start_indx = int(start_seconds * sf)
        end_indx = int(end_seconds * sf)

        # Create the blank figure
        plt.figure(figsize=(10, 4))

        # Plot the graphs
        plt.plot(times[start_indx:end_indx], loc[start_indx:end_indx], color='slategrey', label='LOC')
        plt.plot(times[start_indx:end_indx], roc[start_indx:end_indx], color='grey', label='ROC')
        plt.plot(times[start_indx:end_indx], loc_highlight[start_indx:end_indx], color='indianred')
        plt.plot(times[start_indx:end_indx], roc_highlight[start_indx:end_indx], color='indianred')
        plt.plot(times[start_indx:end_indx], emg[start_indx:end_indx], color="black", label='EMG', lw=1.5)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude (uV)')
        plt.title(f"eye_movements_during_{event_name}")
        plt.legend()
        sns.despine()
        plt.savefig(f"{export_directory}/eog_events-{event_name}.png", bbox_inches='tight',dpi=600)
        plt.close()



"""
events = mne.events_from_annotations(raw)
events_df
events_df = events[0]
events[1]
"""
