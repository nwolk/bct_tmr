#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This code will run a chi square analysis -- specifically to see
if completing two different tasks has a statistically significant
effect on the amount of lucid dreams a participant has. It will
also create a graph showing how many participants became lucid
based on the task.

A data table with the results of this analysis will be exported
to a CSV file on my computer called "ChiSquareAnalysisResults."
A graph will be saved as "chi2graph.png."

"""

# # DEFINE FILENAMES

bct_tmr_data = '../data/bct_tmr_data.csv'
final_data = '../results/ChiSquareAnalysisResults.csv'
final_graph = '../results/chi2graph.png'

# # IMPORT PACKAGES

from scipy.stats import chi2_contingency
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.ion()

# # DEFINE VARIABLES (specific to header names on data file)

had_lucid = "had_lucid"
tmr_condition = "tmr_condition"
participant_id = "participant_id"

# # DEFINE THE TABLE

# put raw data file name and location here
raw_data = pd.read_csv(bct_tmr_data)


# group the data into 2x2 contingency table
# (this adds up how many participants became lucid for each task)
data2x2 = pd.crosstab(index = raw_data['had_lucid'],
                   columns=raw_data['tmr_condition'],
                   margins=False)

# # RUN CHI SQUARE ANALYSIS
stat, p, dof, expected = chi2_contingency(data2x2)

# # IF NEEDED, UNCOMMENT THE CODE BELOW TO INTERPRET AND PRINT THE P VALUE
# alpha = 0.05
# print("p value is " + str(p))
# if p <= alpha:
#  	print('Dependent (reject null hypothesis)')
# else:
#  	print('Independent (null hypothesis holds true)')

# # SAVE RESULTS AS CSV

# define sample size and create results table
sample = raw_data["participant_id"].nunique()
final_table = pd.DataFrame({
    "Statistic": ["DOF", "Sample Size", "P Value"],
    "Value": [dof, sample, p]
})

# move the results table to csv file
export_filename = final_data
final_table.to_csv(export_filename, index = False, float_format="%.6f")

# # CREATE GRAPH OF RESULTS

sns.set_theme(style="whitegrid")

graph_data = pd.read_csv(bct_tmr_data)
graph_data = graph_data.replace({"tmr_condition": {'bct': "Mindfulness Task", 'svp':"Attention Task"}})

# Draw plot
g = sns.catplot(
    data=graph_data, kind="count",
    hue="tmr_condition", x="had_lucid",
    ci=95, palette="muted", alpha=.6, height=6
)

g.despine(left=True)
g.set_axis_labels(" ", "Number of Participants")
g.legend.set_title("TMR Condition")
plt.xticks([0, 1], ["No Lucid Dream", "Lucid Dream"])
# plt.title("Results")

plt.savefig(final_graph, bbox_inches='tight',dpi=600)
plt.close()
