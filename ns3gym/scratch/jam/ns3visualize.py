#! /usr/bin/python3

import os
import argparse
import subprocess
import pandas as pd
import matplotlib.pyplot as plt


def extract_features(node_id: int, experiment_path: os.path, fields: list[str]) -> pd.DataFrame:
    """
    This function reads a "node_i_traceall.txt" file and return a DataFrame with columns determined by the fields parameter
    :param1 node_id: The id of the node to determine the file name
    :param2 experiment_path: The path to the experiment results' folder
    :param3 fields: A list of strings containing field names to be extracted
    :return result: A DataFrame with the columns listed in fields
    """
    file_name = f"{experiment_path}/node_{node_id}_traceall.txt"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, skiprows=1,
                         delimiter="\t", index_col=8)
        df = df.rename(columns=lambda x: x.strip())
        result = df.loc[df["channelNumber"] == 178, fields]
        return result
    else:
        raise FileNotFoundError


def calculate_QoS(df: pd.DataFrame):
    df["QoS"] = (df["number of neighbors"] - df["ls"]) / df["lc"]
    df.loc[df["lc"] == 0, "QoS"] = df.loc[df["lc"] == 0, "number of neighbors"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=int)
    parser.add_argument("--node", "-n", default=9, type=int)
    args = parser.parse_args()

    experiment_folder = f"/usr/ns3-gym/GUSTtracefiles/experiment_{args.experiment}"

    # Run the experiment if the folder does not exist
    if os.path.exists(experiment_folder):
        print(f"experiment_{args.experiment} already exists.")
    else:
        os.mkdir(experiment_folder)

        # Run waf
        p = subprocess.Popen(
            ["/usr/ns3-gym/waf", "--run", f"jam --p=1 --N=10 --scenario=1 --agentNum=0 --exp={args.experiment}"])
        p.wait()

    # Plot QoS for a specific node
    try:
        print(
            f"Plotting QoS for node {args.node} of experiment {args.experiment}")
        df = extract_features(args.node, experiment_folder, fields=[
            "ls", "lc", "number of neighbors", "label(jammed or not)"])

        calculate_QoS(df)

        plt.plot(df["QoS"])
        plt.savefig(experiment_folder + f"/QoS_of_node_{args.node}")
    except FileNotFoundError:
        print(f"Experiment {args.experiment} does not have node {args.node}")