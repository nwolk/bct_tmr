"""
Use this code to analyze breath counting task data. It will compare BCT
performance before vs. after sleep to see if participants showed improvement
on this task. The analysis is done by counting each cycle as either correct
(all 9 presses were correct) or incorrect (at least one press was an overshoot
or undershoot), and self caught mistakes with all other presses correct
counting as correct. These values were then averaged to get two accuracy
values per participant, one for before sleep and one for after sleep. A t-test
and wilcoxon test are done to determine statistical significance. This code
uses a .csv file with data about each button press each participant made and
if it was correct or not.
"""

# import packages

import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
import seaborn as sns

# define variables

export_directory = '../results'
export_fname_1 = f"{export_directory}/tmr_t-test_results.csv"
export_fname_2 = f"{export_directory}/tmr_wilcoxon_results.csv"
export_fname_3 = f"{export_directory}/tmr_t-test_graph.png"

raw_data = f'../data/task-bct_agg.csv'

# find average value for accuracy per acquisition (pre or post)

df = pd.read_csv(raw_data)

data_frame = (
    df.groupby(["participant_id", "acquisition_id", "cycle"])
    ["accuracy"].last()  # extract the accuracy of the last press of the trial
    .eq("correct")  # convert to boolean (ie, True if correct, False if not)
    .groupby(["participant_id", "acquisition_id"]).mean()  # Convert to pct correct for each participant
)
data_frame = data_frame.unstack(level = -1).dropna()

# run paired t-test and wilcoxon test

ttest = pg.ttest(data_frame['acq-post'], data_frame['acq-pre'], paired = True)
ttest.to_csv(export_fname_1)

wilcoxon = pg.wilcoxon(data_frame['acq-post'], data_frame['acq-pre'])
wilcoxon.to_csv(export_fname_2)

# create graph

long_data = data_frame.melt(
    value_vars=["acq-post", "acq-pre"], var_name="acquisition_id")

g = sns.catplot(
    data=long_data,
    x="acquisition_id",
    y="value",
    palette="pastel",
    kind="bar",
    order=["acq-pre", "acq-post"],
)

g.despine(left=True)
g.set_axis_labels("Acquisition", "Accuracy")
plt.title("TMR Results")

plt.savefig(export_fname_3, bbox_inches='tight',dpi=600)
plt.close()
