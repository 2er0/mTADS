from pathlib import Path

import pandas as pd
import yaml


def load_all_stored_datasets(benchmark: str = "fsb"):
    if benchmark == "fsb":
        base_path = f"{Path(__file__).parent}/fsb_timeseries"
    elif benchmark == "srb":
        base_path = f"{Path(__file__).parent}/srd_timeseries"
    else:
        raise ValueError(f"Benchmark suite '{benchmark}' not available")
    print(base_path)
    dataset_cache = {}
    configs = {}
    for c in Path(base_path).glob("*.yaml"):
        with open(c, "r+") as f:
            config = yaml.safe_load(f)
            name = list(filter(lambda x: "timeseries" in x, config.keys()))[0]
            for sequence in config[name]:
                sequence["origin"] = c.name
                configs[sequence["name"]] = sequence

    def _reduce_cache():
        remove_list = []
        for k, v in dataset_cache.items():
            v["cache"] -= 1
            if v["cache"] <= 0:
                remove_list.append(k)
        for r in remove_list:
            dataset_cache.pop(r)

    def _drop_not_relevant_columns(df: pd.DataFrame):
        return df.loc[:, ~df.columns.str.startswith('permutation_')]

    def _load_from_path(path):
        if path.name in dataset_cache:
            # update cache counter
            dataset_cache[path.name]["cache"] = 5
            cache_entry = dataset_cache[path.name]
            return path.name, configs[path.name], \
                cache_entry["train_no_anomaly"], cache_entry["train"], cache_entry["test"]
        else:
            train_no_anomaly_sequence = Path(f"{path}/train_no_anomaly.csv")
            train_sequence = Path(f"{path}/train_anomaly.csv")

            if train_no_anomaly_sequence.exists():
                train_no_anomaly_sequence = _drop_not_relevant_columns(pd.read_csv(train_no_anomaly_sequence.absolute()))
            else:
                train_no_anomaly_sequence = None

            if train_sequence.exists():
                train_sequence = _drop_not_relevant_columns(pd.read_csv(train_sequence.absolute()))
            else:
                raise FileExistsError("Train sequence not available")

            test_sequence = Path(f"{path}/test.csv")
            if test_sequence.exists():
                test_sequence = _drop_not_relevant_columns(pd.read_csv(test_sequence.absolute()))
            else:
                raise FileExistsError("Test sequence not available")

            dataset_cache[path.name] = {"cache": 5,
                                        "train_no_anomaly": train_no_anomaly_sequence,
                                        "train": train_sequence,
                                        "test": test_sequence}

            return path.name, configs[path.name], train_no_anomaly_sequence, train_sequence, test_sequence

    sorted_dataset_list = sorted(list(Path(base_path).glob("*")))
    for p in sorted_dataset_list:
        if Path(p).is_dir():
            _reduce_cache()
            name, config, train_no_anomaly, train, test = _load_from_path(p)
            if train_no_anomaly is not None:
                yield name + "-no-anomaly", config, train_no_anomaly, test
            yield name, config, train, test


if __name__ == "__main__":
    # find index of a sequence to seek to a start or end point
    sets = list(load_all_stored_datasets("fsb"))
    for i, (n, c, _, _) in enumerate(sets):
        if n == '2-corr-0.5_mInfluence-0.0_inclTrend-1_channel_anomaly':
            print(i, n, c)
