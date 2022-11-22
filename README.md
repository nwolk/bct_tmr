# bct_tmr

Analyzes EEG and lucid dream data to determine if a mindfulness task induced lucid dreams

Main analyses:
1. Chi square test on number of subs that got lucid across conditions
2. T-test to determine if subjects' breathing changed from before to after a cue

---

## Setup directories

    /bct_tmr
    /bct_tmr/code
    /bct_tmr/data
    /bct_tmr/results


## General sequence of scripts

    # runs a chi square analysis using a CSV file of lucid data by subject
    python chi2script.py              ## outputs /bct_tmr/results/chi2graph.png
                                      ## outputs /bct_tmr/results/ChiSquareAnalysisResults.png

    # automatically finds sleep stages from EEG data for 1 subject at a time
      # uses argparse to make graphs per subject, put subject number in terminal
    python sleep_staging_script.py    ## outputs /bct_tmr/results/{subject}events_graph.png
                                      ## outputs /bct_tmr/results/{subject}hypno_graph.png
                                      ## outputs /bct_tmr/results/{subject}prob_graph.png
                                      ## outputs /bct_tmr/results/{subject}hypnogram_data.csv

    # detects rapid eye movements in EEG data for 1 subject at a time
    python rem_detection.py           ## outputs /bct_tmr/results/{subject}hypnogram_data.csv
                                      ## outputs /bct_tmr/results/eog_events-{event_name}.png

    # runs an analysis on respiration data to determine if breathing changed before vs. after a cue
    python resp_analysis.py           ## outputs /bct_tmr/results/signal_table_{sub_str}_{count}.csv
                                      ## outputs /bct_tmr/results/rrv_table_{sub_str}_{count}.csv

    # runs a t-test from previous script's data tables
    python t-test_resp.py             ## outputs /bct_tmr/results//t-test_graph.csv
                                      ## outputs /bct_tmr/results/t-test_results.png
