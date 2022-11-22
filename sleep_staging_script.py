"""
This code takes raw EEG data and automatically stages sleep. It will create
three graphs: a hypnogram, a graph with how confident it is on its sleep
staging, and a graph with experimental events and when they occured. It will
also detect experimental events, like cues, and plot the exact time those
events occured on the hypnogram. It will also save the probability of each
sleep stage per epoch.

The two graphs will be saved as PNGs and the hypnogram data per epoch
will be saved as a CSV file. All files will be saved to my 'programs' folder.

"""

# # START COMMAND-LINE PARSING

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--subject")
args = parser.parse_args()
print(args.subject)

# # CREATE VARIABLES

subject = args.subject

eeg_data = f'../data/sub-{subject}_ses-001_eeg.cnt'
events_plot = f'../results/{subject}events_graph.png'
hypnogram_final = f'../results/{subject}hypno_graph.png'
probability_graph = f'../results/{subject}prob_graph.png'
hypnogram_csv = f'../results/{subject}hypnogram_data.csv'

# # IMPORT PACKAGES

import mne
import yasa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# # DEFINE VARIABLES

eeg_name = "Cz"
eog_name = "R-HEOG"
emg_name = "EMG"
sf_freq = 100

cue_event_number = 22

# # LOADING AND PROCESSING DATA

# Loading in data directly as an MNE Raw object
raw = mne.io.read_raw_cnt(eeg_data, preload=True, verbose=False)

# Downsample the data to 100 Hz
raw.resample(sf_freq)
# Apply a bandpass filter from 0.1 to 40 Hz
raw.filter(0.1, 40)
# Select a subset of EEG channels
# raw.pick_channels(['Cz', 'R-HEOG'])

# Printing channel names and sampling frequency
print('The channels are:', raw.ch_names)
print('The sampling frequency is:', raw.info['sfreq'])

# Specifying which channel names I will use
sls = yasa.SleepStaging(raw, eeg_name = eeg_name, eog_name = eog_name, emg_name = emg_name)

# Getting the predicted sleep stages
hypno = sls.predict()
int_hypno = yasa.hypno_str_to_int(hypno)

# Detecting experimental events (like cues)
events, event_ids = mne.events_from_annotations (raw)
print(events[:5])  # show the first 5

# Plotting experimental events
fig = mne.viz.plot_events(events, show=False)
plt.savefig(events_plot, bbox_inches='tight',dpi=600)
plt.close()

# # PLOTTING CUES ON HYPNOGRAM

# Naming columns on DataFrame
events_df = pd.DataFrame(events, columns=["time", "duration", "type_of_event"])

# Converting to dataframe of events to hours to match hypnogram
events_df["time"] = events_df["time"] / sf_freq / 60 / 60

# Pulling out a specific event
cue_event_df = events_df.query(f"type_of_event=={cue_event_number}")

# new_dataframe = events_df.query("type_of_event==30")

# Creating a variable with just the time stamps and converting it to a list
cue_time_column = cue_event_df['time']
cue_time_final = cue_time_column.tolist()

# Plotting the hypnogram
ax = yasa.plot_hypnogram(int_hypno)

# Plotting events on hypnogram
ax.vlines(cue_time_final, ymin = -5, ymax = 1, color = "green", label="Cues")
plt.legend()

# Saving hypnogram as PNG
plt.savefig(hypnogram_final, bbox_inches='tight',dpi=600)
plt.close()

# # PLOTTING PROBABILITY/CONFIDENCE GRAPH

# Plot the predicted probabilities
sls.plot_predict_proba();

# Saving predicted probabilities as PNG
plt.savefig(probability_graph, bbox_inches='tight',dpi=600)
plt.close()

# Defining confidence
confidence = sls.predict_proba().max(1)

# Creating a dataframe with the predicted stages and confidence
df_pred = pd.DataFrame({'Stage': hypno, 'Confidence': confidence})

# Exporting to a CSV file
df_pred.to_csv(hypnogram_csv)
