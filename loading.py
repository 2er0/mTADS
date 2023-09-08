from pathlib import Path
from shutil import rmtree

import pandas as pd
import yaml
from requests import get
import zipfile

default_benchmark_path = {"fsb": f"{Path(__file__).parent}/fsb_timeseries",
                          "srb": f"{Path(__file__).parent}/srd_timeseries"}
base_url = "https://github.com/2er0/mTADS/releases/download/v1.0/"
benchmark_file_name = {"fsb": "fsb_timeseries.zip",
                       "srb": "srb_timeseries.zip"}


def get_default_path(benchmark: str = "fsb"):
    try:
        return default_benchmark_path[benchmark]
    except KeyError:
        raise ValueError(f"Benchmark suite '{benchmark}' not available")


def check_suite_availability(benchmark: str = "fsb"):
    base_path = Path(get_default_path(benchmark))
    if base_path.exists() and len(list(base_path.glob("*.yaml"))) > 0 and len(list(base_path.glob("*/**.csv"))) > 0:
        # all good
        print(f"Benchmark suite {benchmark} is available.")
        return

    # clean
    download_dir = f"{Path(__file__).parent}/download/"
    # clean previously downloaded
    rmtree(f"{download_dir}{benchmark_file_name[benchmark]}", ignore_errors=True)
    # clean benchmark folder
    rmtree(default_benchmark_path[benchmark], ignore_errors=True)

    # setup folders
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    Path(default_benchmark_path[benchmark]).mkdir(parents=True, exist_ok=True)

    # download
    print(f"Downloading benchmark suite: {benchmark}")
    r = get(f"{base_url}{benchmark_file_name[benchmark]}", stream=True)
    suite_archive = f"{download_dir}{benchmark_file_name[benchmark]}"
    with open(suite_archive, "wb") as f:
        f.write(r.content)

    # unzip
    print(f"Extracting {benchmark} suite")
    with zipfile.ZipFile(suite_archive, 'r') as zip_ref:
        zip_ref.extractall(f"{Path(__file__).parent}")


def load_all_stored_datasets(benchmark: str = "fsb"):
    # check suite availability
    check_suite_availability(benchmark)
    # run suite iterator
    base_path = get_default_path(benchmark)
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
                train_no_anomaly_sequence = _drop_not_relevant_columns(
                    pd.read_csv(train_no_anomaly_sequence.absolute()))
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
        if n == '2-saw-all-no-anomaly':
            print(i, n, c)
