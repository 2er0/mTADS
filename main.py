import argparse
import random
from pathlib import Path
from shutil import rmtree

import yaml
from tqdm import tqdm

from generators import *

random.seed(42)
np.random.seed(42)

# [3]
SIMPLE_INCREASING = [
    generate_simple_increasing_data,
    generate_saw_data,
    generate_4_saw_data,
]

# [12]
STD_CUT_INCREASING = [
    *[generate_std_cut_increasing_data_dynamic(2, i) for i in [10, 40, 70]],
    *[generate_std_cut_increasing_data_dynamic(3, i) for i in [10, 40, 70]],
    *[generate_std_cut_continue_increasing_data_dynamic(2, i) for i in [10, 30, 50]],
    *[generate_std_cut_continue_increasing_data_dynamic(3, i) for i in [10, 30, 50]]
]

# [8]
WAVE = [
    generate_simple_wave_data,
    generate_synced_wave_data,
    generate_off_synced_wave_data,
    generate_light_off_synced_wave_data,
    # 4
    generate_4_simple_wave_data,
    generate_no_synced_cut_wave_data,
    generate_medium_past_std_cut_wave_data,
    generate_big_past_std_cut_wave_data
]

# [5]
# Published version of this sequences can not be regenerated
# They were added later and not in a full generation run
CORRELATION = [
    generate_correlation_data,
    generate_correlation_2_data,
    generate_correlation_2_trend_data,
    generate_correlation_2_trend_strong_data,
    # 4
    generate_correlation_2_high_corr_data
]

# [6]
STD_CUT_WAVE = [
    generate_std_cut_wave_data_dynamic(sequences, pre_std_ration, pre_std_past)
    for sequences in [2, 4]
    for pre_std_ration in [2]
    for pre_std_past in [10, 30, 70]]

# [34]
ALL_BASE = [*SIMPLE_INCREASING, *WAVE, *STD_CUT_INCREASING, *STD_CUT_WAVE, *CORRELATION]

# [4]
PREDATOR_PRAY = [
    generate_4_3_prey_2_predator_500_cooldown_1_mil_steps,
    generate_4_3_prey_2_predator_300_cooldown_short,
    generate_4_2_prey_2_predator_1000_cooldown_1_mil_steps,
    generate_4_2_prey_2_predator_300_cooldown_short
]

ALL_ADVANCED = [*PREDATOR_PRAY]

suite_config = {
    "FSB": ALL_BASE,
    "SRB": ALL_ADVANCED
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", type=str, default="FSB", choices=['FSB', 'SRB'],
                        help="Name name of the benchmark suite to generate: 'FSB' or 'SRB'")
    parser.add_argument("--save", type=str, default="yes",
                        help="Save the generated sequences: 'yes' or 'no'")
    parser.add_argument("--plot", type=str, default="yes",
                        help="Render each sequences after generation: 'yes' or 'no'")
    parser.add_argument("--interactive", type=str, default="no",
                        help="Generate sequences interactively with with user input to continue: 'yes' or 'no'")
    parser.add_argument("--remove_orphan_only", type=str, default="no",
                        help="Remove orphan sequences only: 'yes' or 'no'")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    suite = str(args.suite).lower()
    name = f"{suite}-timeseries"
    base_path = name.replace("-", "_")
    LIST = suite_config[args.suite]

    plot = args.plot == "yes"
    if args.remove_orphan_only == "no":
        configs = {name: []}
        for i, f in tqdm(enumerate(LIST)):
            df, params, group = f(plot=plot)
            try:
                df_no_anomaly, _, _ = f(anomaly=False, plot=plot)
            except TypeError as e:
                print(i, f, e)
            if args.save == "yes":
                params["name"] = group
                configs[name].append(params)
                # remove existing folder
                if Path(f"{base_path}/{group}").exists():
                    rmtree(f"{base_path}/{group}", ignore_errors=False)
                # save new stuff
                Path(f"{base_path}/{group}").mkdir(parents=True, exist_ok=True)
                # save training without anomaly
                df_no_anomaly.to_csv(f"{base_path}/{group}/train_no_anomaly.csv", sep=",", index=False)
                # save training
                df.to_csv(f"{base_path}/{group}/train_anomaly.csv", sep=",", index=False)
                # save test
                df, _, _ = f(plot=plot)
                df.to_csv(f"{base_path}/{group}/test.csv", sep=",", index=False)
            if args.interactive == "yes":
                print(f'Showing: {group}')
                input('Next <Enter>')
            pass
        pass

        if args.save == "yes":
            if Path(f"{base_path}/overview.yaml").exists():
                Path(f"{base_path}/overview.yaml").unlink()
            with open(f"{base_path}/overview.yaml", "w+") as f:
                yaml.dump(configs, f, allow_unicode=True)

    # clean up orphan sequences
    print("Cleaning up orphan sequences from suite")
    datasets_folders = []
    for c in Path(f"{base_path}").glob("*.yaml"):
        with open(c, "r+") as f:
            config = yaml.safe_load(f)
            name = list(filter(lambda x: "timeseries" in x, config.keys()))[0]
            for t in config[name]:
                datasets_folders.append(t["name"])

    for d in Path(f"{base_path}").glob("*"):
        if d.is_dir():
            if d.name not in datasets_folders:
                print(f"Removing orphan sequence: {d}")
                rmtree(d, ignore_errors=False)
