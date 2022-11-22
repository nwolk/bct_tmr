"""
Respiration Analysis Part 2

This code uses the RRV tables created in my resp_analysis script. It
will read through all of these files, take out the specific row I want
and run a t-test on this data. It will also average all the data across
participants and create a bar graph to visualize these results. 
"""

# import packages

import pingouin as pg
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# define variables

export_directory = '../results'
export_fname_1 = f"{export_directory}/t-test_graph.csv"
export_fname_2 = f"{export_directory}/t-test_results.png"

# find all RRV files from resp_analysis script results

cwd = '/Users/norahwolk/Desktop/bct_tmr/results'
files = os.listdir(cwd)
rrv_files = []
for file in files:
    if file.startswith('rrv_table')==True:
        rrv_files.append(file)

df = []

# read all RRV CSV files

for rrv_file in rrv_files:
    a = '/'
    data = pd.read_csv(cwd + a + rrv_file, skiprows=0, nrows=1)
    data['id'] = os.path.basename(rrv_file)
    df.append(data)

# create table with all cues and subjects, group table by subject number

df = pd.concat(df, axis = 0, ignore_index = True)

# use string to get subject number
df["subject"] = df["id"].str.split("-").str[1].str.split("_").str[0].astype(int)

subject_table = df.groupby("subject")[['cue', 'uncued']].mean()

# run t-test

pg.ttest(subject_table['cue'], subject_table['uncued'])

stats = pg.ttest(subject_table['cue'], subject_table['uncued'], paired=True)
stats.to_csv(export_fname_1)

# convert subject_table from wide to long format

long_data = subject_table.melt(
    value_vars=["cue", "uncued"],
    value_name="RRV_SDBB", var_name="Condition",
)

# graph average breath rate by condition

g = sns.catplot(data = long_data, x="Condition", y="RRV_SDBB", palette = "pastel", kind="bar")

g.despine(left=True)
g.set_axis_labels("Condition", "Respiration Standard Deviation")
plt.title("Results")

plt.savefig(export_fname_2, bbox_inches='tight',dpi=600)
plt.close()
