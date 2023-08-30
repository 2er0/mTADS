import copy
import os

import igraph as ig
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def __simple_plot(t, data):
    fig = plt.figure(figsize=(10, 6))
    axs = fig.subplots(nrows=2, ncols=1, sharex=True)
    for i, d in enumerate(data[:-1]):
        axs[0].plot(t, d, label=f"value-{i}")
    axs[1].plot(t, data[-1], label="anomaly")
    axs[1].set_xlabel('Time')
    axs[0].set_ylabel('Value')
    axs[0].grid()
    axs[1].grid()
    plt.tight_layout()
    plt.legend()
    fig.show()


def __simple_df_plot(data):
    fig = plt.figure(figsize=(10, 6))
    axs = fig.subplots(nrows=2, ncols=1, sharex=True)
    for i in range(data.shape[1] - 2):
        axs[0].plot(data["timestamp"], data[f"value-{i}"], label=f"value-{i}")
    axs[1].plot(data["timestamp"], data["is_anomaly"], label="anomaly")
    axs[1].set_xlabel('Time')
    axs[0].set_ylabel('Value')
    axs[0].grid()
    axs[1].grid()
    plt.tight_layout()
    plt.legend()
    fig.show()


def predator_prey(a=None, b=None, c=None, d=None, pop=None, names=None,
                  rand_th=None, anomaly=None, cooldown=None, periods=10, timestep=0.001,
                  plot=False):
    """
    Multivariate Predator Prey Generator
    :param a: List, alpha, The rate at which prey birth exceeds natural death
    :param b: List/Matrix(row=pred, col=prey), beta, The rate of predation
    :param c: List, gamma, The rate at which predator deaths exceed births without food
    :param d: List/Matrix(row=pred, col=prey), delta, Predator increase with the presence of food
    :param pop: List[List], Initial populations
    :param names: List, Name per sequence
    :param rand_th: Factor when to enable random permutations in the population
    :param anomaly: Include anomalies or not
    :param cooldown: Number of steps until a new anomaly is allowed to occur
    :param periods: The number of periods
    :param timestep: Timestep determines the accuracy of the euler method of integration
    :return:
    """
    if a is None:
        a = [.1]
    if b is None:
        b = [.01]
    if c is None:
        c = [.01]
    if d is None:
        d = [.00002]
    # initial conditions for the rabbit (prey_pop) and fox (predator_pop) populations at time=0
    if pop is None:
        pop = [[1000], [20]]
    if names is None:
        names = ["Rabbits", "Foxes"]

    pop_init = copy.deepcopy(pop)

    is_anomaly = [0]
    random_permutations = [[False] for _ in range(len(pop))]
    random_permutation_change = [0.]
    random_permutation_indexes = []
    permutation = None
    no_permutation_lock_down = None

    # creates a time vector from 0 to end_time, seperated by a timestep
    t = np.arange(1, periods, timestep)
    total_steps = t.shape[0]
    no_anomaly_until = total_steps // 10
    for i in range(1, t.shape[0]):
        pop_update = np.zeros(len(pop))
        # update preys
        # pyi = prey_i
        # pdi = predator_i
        for pyi, a_ in enumerate(a):
            if a_ is not None:
                # birth rate
                current_prey = a_ * pop[pyi][-1]
                for pdi, bs_ in enumerate(b):
                    if bs_ is not None and bs_[pyi] is not None:
                        # predation
                        current_prey -= bs_[pyi] * pop[pyi][-1] * pop[pdi][-1]
                pop_update[pyi] = current_prey * timestep
        # update predators
        for pdi, c_ in enumerate(c):
            if c_ is not None:
                # predator death rate
                current_pred = -(c_ * pop[pdi][-1])
                for pyi, ds_ in enumerate(d[pdi]):
                    if ds_ is not None:
                        # predation birth rate
                        current_pred += ds_ * pop[pyi][-1] * pop[pdi][-1]
                pop_update[pdi] += current_pred * timestep

        for j in range(len(pop)):
            n_pop = pop[j][-1] + pop_update[j]
            if n_pop < 0:
                n_pop = 0
            pop[j].append(n_pop)

        # track permutations
        for j in range(len(pop)):
            random_permutations[j].append(False)
        is_anomaly.append(0)
        random_permutation_change.append(0.)
        # execute permutations
        if permutation is not None:
            # track injected anomaly
            random_permutations[permutation["pop"]][-1] = True
            is_anomaly[-1] = True
            random_permutation_change[-1] = permutation["amount"]
            random_permutation_indexes.append(i)
            # apply anomaly
            temp_population = pop[permutation["pop"]][-1]
            pop[permutation["pop"]][-1] += permutation["amount"]
            # do control softening of the anomaly
            temp_amount = permutation["amount"]
            permutation["amount"] -= permutation["reduction"]
            if plot:
                print(i, "|", permutation["pop"], "|", "Pop.:", temp_population, ">", pop[permutation["pop"]][-1], "|",
                      "Perm.:", temp_amount, ">", permutation["amount"], "=", permutation["reduction"])
            permutation["steps"] -= 1
            # stop adding an anomaly if the population died
            if pop[permutation["pop"]][-1] < 0:
                pop[permutation["pop"]][-1] = 0
                permutation["steps"] = 0

            if permutation["steps"] <= 0 or \
                    np.abs(np.diff([permutation["amount"], permutation["original_amount"]])[0]) >= \
                    np.abs(permutation["original_amount"]):
                permutation = None
                no_permutation_lock_down = cooldown
                continue

        if anomaly and rand_th is not None and i > no_anomaly_until:
            if permutation is None and no_permutation_lock_down is None and np.random.random() >= rand_th:
                # determine the direction of the anomaly
                permutation_direction = 1 if np.random.random() >= 0.5 else -1
                # determine which population to inject an anomaly
                pop_select = np.random.randint(0, len(pop))
                # population died-out = continue
                if pop[pop_select] == 0:
                    continue
                # determine the length of the anomaly
                permutation_steps = np.random.randint(20, 30)
                # determine the magnitude of the anomaly
                permutation_amount = np.random.randint(4, 7) * 0.02
                permutation_amount *= permutation_direction
                # determine a factor to soften the anomaly impact over time
                permutation_reduction = np.random.randint(2, 5) * 0.001
                permutation_reduction *= permutation_direction

                permutation = {
                    "pop": pop_select,
                    "steps": permutation_steps,
                    "amount": permutation_amount,
                    "reduction": permutation_reduction,
                    "original_amount": permutation_amount
                }
        if no_permutation_lock_down is not None:
            no_permutation_lock_down -= 1
            if no_permutation_lock_down <= 0:
                no_permutation_lock_down = None

    feature_columns = []
    data_dict = {}
    data_dict["timestamp"] = t
    for i, p in enumerate(pop):
        data_dict[f"value-{i}"] = p
        feature_columns.append(f"value-{i}")
    for i, p in enumerate(random_permutations):
        data_dict[f"permutation {names[i]}".replace(" ", "_")] = p
    data_dict["permutation_value"] = random_permutation_change
    data_dict["is_anomaly"] = is_anomaly

    df = pd.DataFrame(data_dict)

    parameters = {
        "names": list(names),
        "rand_th": rand_th, "periods": periods, "cooldown": cooldown,
        "timestep": timestep,
        "permutation": sorted(list(set(random_permutation_indexes))),
        "feature_columns": feature_columns,
        "channels": len(feature_columns),
        "anomalies": [{"kinds": [{"kind": "nature"}]}]
    }

    if plot:
        """ visualization """
        # visualization of deterministic populations against time
        plt.figure(figsize=(40, 20))
        for p in pop:
            plt.plot(t, p)
        x_scatter = []
        y_scatter = []
        for i, row in enumerate(zip(*random_permutations)):
            for j, col in enumerate(row):
                if col:
                    x_scatter.append(t[i])
                    y_scatter.append(pop[j][i])

        plt.scatter(x_scatter, y_scatter, c="black", alpha=0.3)
        plt.xlabel('Time')
        plt.ylabel('Population Size')
        plt.legend(names)
        plt.grid()
        plt.title('Deterministic Lotka-Volterra')
        plt.tight_layout()
        plt.show()

    return df, parameters, f"{len(pop)}-lotka_volterra"


def generate_4_3_prey_2_predator_500_cooldown_1_mil_steps(rand_th=None, anomaly=True,
                                                          cooldown=500, periods=1000,
                                                          plot=False):
    if rand_th is None:
        rand_th = 0.99999
    df, parameters, group = predator_prey(a=(0.2, 0.2, 0., None),
                                          b=(None,
                                             None,
                                             (.004, .003, 0., None),
                                             (.002, .003, .002, None)),
                                          c=(None, None, .14, .14),
                                          d=(None,
                                             None,
                                             (.001, 0.001, None, None),
                                             (None, 0.001, 0.001, None)),
                                          pop=[[80], [60], [20], [10]],
                                          names=("Prey 1", "Prey 2",
                                                 "Prey 3/Pred 1", "Pred 2"),
                                          rand_th=rand_th,
                                          cooldown=cooldown,
                                          periods=periods,
                                          anomaly=anomaly,
                                          plot=plot)
    return df, parameters, f"{group}-3-prey-2-predator-500-cooldown-1-mil-steps"


def generate_4_3_prey_2_predator_300_cooldown_short(rand_th=0.99998, anomaly=True, plot=False):
    periods = 200
    cooldown = 300
    df, parameters, group = generate_4_3_prey_2_predator_500_cooldown_1_mil_steps(
        rand_th=rand_th, anomaly=anomaly, cooldown=cooldown, periods=periods, plot=plot
    )

    return df, parameters, group.replace("500", "300").replace("1-mil-steps", "short")


def generate_4_2_prey_2_predator_1000_cooldown_1_mil_steps(rand_th=None, anomaly=True,
                                                           cooldown=1000, periods=1000,
                                                           plot=False):
    if rand_th is None:
        rand_th = 0.99999
    df, parameters, group = predator_prey(a=(0.3, 0.25, None, None),
                                          b=(None,
                                             None,
                                             (.003, None, None, None),
                                             (None, .002, None, None)),
                                          c=(None, None, .14, .13),
                                          d=(None,
                                             None,
                                             (.002, None, None, None),
                                             (.0005, .002, None, None)),
                                          pop=[[80], [60], [20], [10]],
                                          names=("Prey 1", "Prey 2",
                                                 "Pred 1", "Pred 2"),
                                          rand_th=rand_th,
                                          cooldown=cooldown,
                                          periods=periods,
                                          anomaly=anomaly,
                                          plot=plot)
    return df, parameters, f"{group}-2-prey-2-predator-1000-cooldown-1-mil-steps"


def generate_4_2_prey_2_predator_300_cooldown_short(rand_th=0.99998, anomaly=True, plot=False):
    periods = 200
    cooldown = 300
    df, parameters, group = generate_4_2_prey_2_predator_1000_cooldown_1_mil_steps(
        rand_th=rand_th, anomaly=anomaly, cooldown=cooldown, periods=periods, plot=plot
    )

    return df, parameters, group.replace("1000", "300").replace("1-mil-steps", "short")


def generate_simple_increasing_data(a_t=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 0.99]

    parameters = {
        "a_t": a_t,
        "feature_columns": ["value-0", "value-1"],
        "channels": 2,
        "anomalies": [{"kinds": [{"kind": "signal-cancellation"}]}]
    }

    def next_value(a_x, value):
        return a_x * value + np.random.random()

    data = [[0], [0], [0]]
    t = [0]
    for i in range(1, 1000):
        t.append(i)
        data[0].append(next_value(a_t[0], data[0][-1]))
        data[1].append(next_value(a_t[1], data[1][-1]))
        data[2].append(0)
    if anomaly:
        data[-1][-1] = 1
        a_0 = [0, 0]
        for i in range(100):
            t.append(1000 + i)
            data[0].append(0)
            data[1].append(0)
            data[2].append(1)
    else:
        for i in range(100):
            t.append(1000 + i)
            data[0].append(next_value(a_t[0], data[0][-1]))
            data[1].append(next_value(a_t[1], data[1][-1]))
            data[2].append(0)

    if plot:
        __simple_plot(t, data)

    return pd.DataFrame({"timestamp": t,
                         "value-0": data[0], "value-1": data[1],
                         "is_anomaly": data[-1]}), parameters, "2-increasing-all"


def generate_saw_data(a_t=None, cuts=None, iterations=None, inject=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 0.99]
    if cuts is None:
        cuts = [100, 133]
    if iterations is None:
        iterations = 1000
    if inject is None:
        inject = 0.8

    anomaly_start = int(iterations * inject)
    current_cuts = [cuts[0] for c in cuts]

    if not anomaly:
        for i in range(1, len(a_t)):
            a_t[i] = a_t[0]
            cuts[i] = cuts[0]

    parameters = {
        "a_t": a_t,
        "cuts": cuts,
        "inject": inject,
        "iterations": iterations,
        "permutation": [],
        "feature_columns": [f"value-{i}" for i in range(len(a_t))],
        "channels": len(a_t),
        "anomalies": [{"kinds": [{"kind": "signal-reset"}]}]
    }

    def next_value(a_x, value):
        return a_x * value + np.random.random()

    data = [[0] for _ in range(len(a_t) + 1)]
    t = [0]
    for i in range(1, iterations):
        if i > anomaly_start:
            current_cuts = cuts
        t.append(i)
        data[-1].append(0)
        for j in range(len(a_t)):
            if i % current_cuts[j] == 0:
                if anomaly and i > anomaly_start:
                    data[j].append(0)
                    parameters["permutation"].append(i)
                else:
                    data[j].append(0)
            else:
                data[j].append(next_value(a_t[j], data[j][-1]))

    parameters["permutation"] = sorted(list(set(parameters["permutation"])))
    for p in parameters["permutation"]:
        for i in range(p - 1, p + 2):
            data[-1][i] = 1

    if plot:
        __simple_plot(t, data)

    pre_df = {"timestamp": t}
    for i in range(len(cuts)):
        pre_df[f"value-{i}"] = data[i]
    pre_df["is_anomaly"] = data[-1]

    return pd.DataFrame(pre_df), parameters, f"{len(a_t)}-saw-all"


def generate_saw_long_data(a_t=None, cuts=None, iterations=None, inject=None, anomaly=True, plot=False):
    if iterations is None:
        iterations = 10000
    df, parameters, group = generate_saw_data(a_t, cuts, iterations, inject, anomaly, plot)
    return df, parameters, group.replace("all", "long-all")


def generate_4_saw_data(a_t=None, cuts=None, iterations=None, inject=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 0.99, 0.98, 0.97]
    if cuts is None:
        cuts = [100, 133, 142, 151]

    df, parameters, group = generate_saw_data(a_t, cuts, iterations, inject, anomaly, plot)
    return df, parameters, group


def generate_4_long_saw_data(a_t=None, cuts=None, iterations=None, anomaly=True, plot=False):
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_saw_data(a_t, cuts, iterations, anomaly, plot)
    return df, parameters, group.replace("all", "long-all")


def generate_simple_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 1.5]
    if cuts is None:
        cuts = [7, None]
    if end is None:
        end = 10
    if iterations is None:
        iterations = 1000

    parameters = {
        "a_t": a_t,
        "cuts": cuts,
        "end": end,
        "iterations": iterations,
        "permutation": [],
        "feature_columns": [f"value-{i}" for i in range(len(a_t))],
        "channels": len(a_t),
        "anomalies": [{"kinds": [{"kind": "signal-reset"}]}]
    }

    def next_sequence(a, xs):
        return np.sin(a * xs) + np.random.random(xs.shape[0]) * 0.05

    data = [[] for _ in range(len(a_t) + 1)]
    t = []
    ts = np.linspace(0, end, iterations)
    t.extend(list(range(iterations)))

    for j in range(len(a_t)):
        cut = cuts[j]
        a_ = a_t[j]
        ts_ = ts % cut if anomaly and cut is not None else ts
        x = next_sequence(a_, ts_)
        data[j] = x.tolist()
        if anomaly and cut is not None:
            parameters["permutation"].extend((np.where(np.abs(np.diff(ts_)) > cut - 1)[0] + 1).tolist())

    data[-1].extend([0] * len(data[0]))
    parameters["permutation"] = sorted(list(set(parameters["permutation"])))
    for p in parameters["permutation"]:
        for i in range(p - 1, p + 2):
            if i < iterations:
                data[-1][i] = 1

    if plot:
        __simple_plot(t, data)

    pre_df = {"timestamp": t}
    for i in range(len(a_t)):
        pre_df[f"value-{i}"] = data[i]
    pre_df["is_anomaly"] = data[-1]

    return pd.DataFrame(pre_df), parameters, f"{len(a_t)}-wave-one-channel"


def generate_simple_long_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000
    if cuts is None:
        cuts = [i * 3 for i in [7, 7]]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("all", "all-long")


def generate_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [6.3, 6.3]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("one", "synced-one")


def generate_synced_long_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("synced", "synced-long")


def generate_off_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [6.0, 6.0]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("one", "off-synced-all")


def generate_off_synced_long_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_off_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("off-synced", "off-synced-long")


def generate_light_off_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [6.2, None]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("one", "light-off-synced-one")


def generate_light_off_synced_long_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_light_off_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("light-off-synced", "light-off-synced-long")


def generate_medium_off_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [2.7, 2.7]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("all", "medium-off-all")


def generate_medium_off_long_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_medium_off_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("medium-off", "medium-off-long")


def generate_4_simple_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 1.5, 1.2, 1.8]
    if cuts is None:
        cuts = [7, None, 7, None]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("one", "two")


def generate_4_long_simple_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("all", "long-all")


def generate_4_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 1.5, 0.5, 2]
    if cuts is None:
        cuts = [6.3, 6.3, 6.3, 6.3]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("all", "synced-all")


def generate_4_long_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("synced", "synced-long")


def generate_4_off_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [6.0, 6.0, 6.0, 6.0]

    df, parameters, group = generate_4_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("synced", "off-synced")


def generate_4_long_off_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_off_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("off-synced", "off-synced-long")


def generate_4_light_off_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [6.2, 6.2, 6.2, 6.2]

    df, parameters, group = generate_4_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("synced", "light-off-synced")


def generate_4_long_light_off_synced_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True,
                                               plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_light_off_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("light-off-synced", "light-off-synced-long")


def generate_4_medium_off_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [2.7, 2.7, 2.7, 2.7]

    df, parameters, group = generate_4_synced_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("synced", "medium-off")


def generate_4_long_medium_off_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_medium_off_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("medium-off", "medium-off-long")


def generate_4_flipping_wave_no_cut_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, -1.5, 1.7, -0.7]
    if cuts is None:
        cuts = [14, 15, 16, 17]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("all", "flipping-no-cut-all")


def generate_4_long_flipping_wave_no_cut_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [140, 150, 160, 170]
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_4_flipping_wave_no_cut_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("flipping-no-cut", "flipping-no-cut-long")


def generate_no_synced_cut_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if cuts is None:
        cuts = [6, 8]

    df, parameters, group = generate_simple_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("one", "no-synced-cut-all")


def generate_long_no_synced_cut_wave_data(a_t=None, cuts=None, end=None, iterations=None, anomaly=True, plot=False):
    if end is None:
        end = 100
    if iterations is None:
        iterations = 10000

    df, parameters, group = generate_no_synced_cut_wave_data(a_t, cuts, end, iterations, anomaly, plot)

    return df, parameters, group.replace("no", "no-long")


def generate_std_cut_increasing_data(a_t=None, b_t=None, std_past=None, std_ratio=None, anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 0.99]
    if b_t is None:
        b_t = [1, 0.99]
    if std_past is None:
        std_past = [50, 50]
    if std_ratio is None:
        std_ratio = [1, 1]

    parameters = {
        "a_t": a_t,
        "std_ratio": std_ratio,
        "permutation": [1000] if anomaly else [],
        "feature_columns": ["value-0", "value-1"],
        "channels": 2,
        "anomalies": [{"kinds": [{"kind": "signal-cut"}]}]
    }

    def next_value(a_x, value):
        return a_x * value + np.random.random()

    data = [[0], [0], [0]]
    t = [0]
    for i in range(1, 1000):
        t.append(i)
        data[-1].append(0)
        for j in [0, 1]:
            data[j].append(next_value(a_t[j], data[j][-1]))

    t.append(1000)
    if anomaly:
        data[-1].append(1)
        for j in [0, 1]:
            data[j].append(data[j][-1] - (np.std(data[j][-std_past[j]:]) * std_ratio[j]))
    else:
        data[-1].append(0)
        for j in [0, 1]:
            data[j].append(next_value(a_t[j], data[j][-1]))

    for i in range(99):
        t.append(1001 + i)
        data[-1].append(0)
        for j in [0, 1]:
            data[j].append(next_value(b_t[j], data[j][-1]))

    if plot:
        __simple_plot(t, data)

    return pd.DataFrame({"timestamp": t,
                         "value-0": data[0], "value-1": data[1],
                         "is_anomaly": data[-1]}), parameters, "2-std_cut_increasing"


def generate_std_cut_increasing_data_dynamic(pre_std_ratio, pre_std_past):
    def _gen(a_t=None, b_t=None, std_past=None, std_ratio=None, anomaly=True, plot=False):
        if pre_std_ratio is None:
            raise ValueError("pre_std_ratio needed")
        if pre_std_past is None:
            raise ValueError("pre_std_past needed")
        std_past = [pre_std_past, pre_std_past]
        std_ratio = [pre_std_ratio, pre_std_ratio]

        df, parameters, group = generate_std_cut_increasing_data(a_t, b_t, std_past, std_ratio, anomaly, plot)

        return df, parameters, f"{group}-stdRatio_{pre_std_ratio}-stdPast_{pre_std_past}"

    return _gen


def generate_std_cut_continue_increasing_data_dynamic(pre_std_ratio, pre_std_past):
    def _gen(a_t=None, b_t=None, std_past=None, std_ratio=None, anomaly=True, plot=False):
        if pre_std_ratio is None:
            raise ValueError("pre_std_ratio needed")
        if pre_std_past is None:
            raise ValueError("pre_std_past needed")
        std_past = [pre_std_past, pre_std_past]
        std_ratio = [pre_std_ratio, pre_std_ratio]
        a_t = [0.99, 0.90]
        b_t = [0.99, 0.90]

        df, parameters, group = generate_std_cut_increasing_data(a_t, b_t, std_past, std_ratio, anomaly, plot)

        return df, parameters, f"{group}_continue-stdRatio_{pre_std_ratio}-stdPast_{pre_std_past}"

    return _gen


def generate_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None, iterations=None,
                               anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 1.5]
    if cuts is None:
        cuts = [6.5, 7]
    if std_past is None:
        std_past = [10, 10]
    if std_ratio is None:
        std_ratio = [1, 1]
    if end is None:
        end = 10
    if iterations is None:
        iterations = 1000

    parameters = {
        "a_t": a_t,
        "cuts": cuts,
        "std_ratio": std_ratio,
        "end": end,
        "iterations": iterations,
        "permutation": [],
        "feature_columns": [f"value-{i}" for i in range(len(a_t))],
        "channels": len(a_t),
        "anomalies": [{"kinds": [{"kind": "signal-cut-match"}]}]
    }

    def next_sequence(a, t, noise=1):
        return np.sin(a * t) + noise * np.random.random() * 0.03

    data = [[] for _ in range(len(a_t) + 1)]
    ts = np.linspace(0, end, iterations)
    t_diff = np.mean(np.diff(ts))
    t_diff_half = t_diff / 2

    for j in range(len(a_t)):
        cut = cuts[j]
        a_ = a_t[j]
        t_ = None
        for i, t in enumerate(ts):
            if t_ is None:
                t_ = t
            if anomaly and t_ > 1 and t_ % cut < 0.01:
                # permutation
                parameters["permutation"].append(i)
                last = data[j][-1]
                std = np.std(data[j][-std_past[j]:]) * std_ratio[j]
                # x = last + x_ if last <= 0 else last - x_
                x = last
                while np.abs(np.diff([last, x]))[0] <= std:
                    t_ += t_diff_half
                    x = next_sequence(a_, t_, noise=0)
            else:
                x = next_sequence(a_, t_)
            data[j].append(x)
            t_ += t_diff

    parameters["permutation"] = sorted(list(set(parameters["permutation"])))
    data[-1].extend([0] * len(data[0]))
    for p in parameters["permutation"]:
        for i in range(p - 1, p + 1 + 1):
            if i < iterations:
                data[-1][i] = 1

    if plot:
        __simple_plot(ts, data)

    pre_df = {"timestamp": list(range(iterations))}
    for i in range(len(a_t)):
        pre_df[f"value-{i}"] = data[i]
    pre_df["is_anomaly"] = data[-1]

    return pd.DataFrame(pre_df), parameters, f"{len(a_t)}-std_cut_wave"


def generate_4_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None, iterations=None,
                                 anomaly=True, plot=False):
    if a_t is None:
        a_t = [1, 1.5, -0.6, 0.7]
    if cuts is None:
        cuts = [5, 7, 4.2, 6.2]
    if std_past is None:
        std_past = [20, 20, 20, 20]
    if std_ratio is None:
        std_ratio = [1, 1, 1, 1]

    df, parameters, group = generate_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group


def generate_std_cut_wave_data_dynamic(sequences, pre_std_ratio, pre_std_past):
    pre_a_t = [1, 1.5, -0.6, 0.7]
    cut_multiplier = 6
    pre_cuts = [c * cut_multiplier for c in [5.1, 7, 5.7, 6.2]]

    def _run(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None, iterations=None, anomaly=True, plot=False):
        if sequences is None:
            raise ValueError("sequences needed")
        if pre_std_ratio is None:
            raise ValueError("pre_std_ratio needed")
        if pre_std_past is None:
            raise ValueError("pre_std_past needed")
        std_past = [pre_std_past for _ in range(sequences)]
        std_ratio = [pre_std_ratio for _ in range(sequences)]
        selected = [i for i in range(sequences)]
        a_t = [pre_a_t[i] for i in selected]
        cuts = [pre_cuts[i] for i in selected]

        end = 50
        iterations = 5000

        df, parameters, group = generate_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly,
                                                           plot)

        return df, parameters, f"{group}-stdRatio_{pre_std_ratio}-stdPast_{pre_std_past}"

    return _run


def generate_medium_past_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None,
                                           iterations=None, anomaly=True, plot=False):
    if std_past is None:
        std_past = [20, 20]

    df, parameters, group = generate_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "medium_past_std")


def generate_4_medium_past_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None,
                                             iterations=None, anomaly=True, plot=False):
    if std_past is None:
        std_past = [30, 30, 30, 30]

    df, parameters, group = generate_4_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "medium_past_std")


def generate_big_past_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None, iterations=None,
                                        anomaly=True, plot=False):
    if std_past is None:
        std_past = [30, 30]

    df, parameters, group = generate_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "big_past_std")


def generate_4_big_past_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None,
                                          iterations=None, anomaly=True, plot=False):
    if std_past is None:
        std_past = [40, 40, 40, 40]

    df, parameters, group = generate_4_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "big_past_std")


def generate_double_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None, iterations=None,
                                      anomaly=True, plot=False):
    if std_ratio is None:
        std_ratio = [2, 2]

    df, parameters, group = generate_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "double_std")


def generate_4_double_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None,
                                        iterations=None, anomaly=True, plot=False):
    if std_ratio is None:
        std_ratio = [2, 2, 2, 2]

    df, parameters, group = generate_4_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "double_std")


def generate_tribble_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None, iterations=None,
                                       anomaly=True, plot=False):
    if std_ratio is None:
        std_ratio = [3, 3]

    df, parameters, group = generate_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "tribble_std")


def generate_4_tribble_std_cut_wave_data(a_t=None, cuts=None, std_past=None, std_ratio=None, end=None,
                                         iterations=None, anomaly=True, plot=False):
    if std_ratio is None:
        std_ratio = [3, 3, 3, 3]

    df, parameters, group = generate_4_std_cut_wave_data(a_t, cuts, std_past, std_ratio, end, iterations, anomaly, plot)

    return df, parameters, group.replace("std", "tribble_std")


def generate_correlation_data(alpha=None, cut=None, trend=None, iterations=None, anomaly=True, plot=False):
    """
    Generate correlated random noise sequences.
    Anomalies are expressed by having no correlation between the sequences.
    :param alpha: Matrix of the influence between the channels
    :param cut: List of tuples with start and end of the anomalies
    :param trend: List with magnitude of trend in each channel
    :param iterations: length of the sequence
    :param anomaly: include anomalies in the sequence or not
    :param plot: show the generated sequence
    :return:
    """
    if alpha is None:
        alpha = [[0, 0.5, 0.3, 0],
                 [0, 0, 0.3, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0.3, 0]]
    if iterations is None:
        iterations = 300
    if cut is None:
        cut = [None, [iterations - 20, iterations], None, None]
    if trend is None:
        trend = [0] * len(alpha)

    if not anomaly:
        cut = [None] * len(alpha)

    graph_matrix = np.array(alpha)
    graph_matrix[graph_matrix > 0] = 1
    alpha_t = np.array(alpha).T

    if not np.all(np.hstack(([np.array(alpha_t.shape), len(cut), len(trend)])) == alpha_t.shape[0]):
        raise ValueError("Parameters are not fully compatible")

    r = np.random.rand(iterations, len(alpha))
    trends = np.vstack([np.linspace(0, i, iterations) for i in trend]).T
    r += trends
    is_anomaly = np.full(iterations, 0)

    g = ig.Graph.Adjacency(graph_matrix)
    tree_graph = g.degree(mode="in")

    if 0 not in tree_graph:
        raise ValueError("No independent channel available")
    for node_value in sorted(set(tree_graph)):
        if node_value == 0:
            continue
        for i in range(iterations):
            for n in np.where(np.array(tree_graph) == node_value)[0]:
                if cut[n] is None or i < cut[n][0] or cut[n][1] < i:
                    v = 0
                    for ai, a in enumerate(alpha_t[n, :]):
                        v += a * r[i, ai] + (1 - a) * r[i, n]
                    v /= alpha_t.shape[0]
                    r[i, n] = v
                else:
                    is_anomaly[i] = 1

    data = {"timestamp": list(range(iterations))}
    for i in range(alpha_t.shape[0]):
        data[f"value-{i}"] = r[:, i]
    data["is_anomaly"] = is_anomaly

    df = pd.DataFrame.from_dict(data)

    if plot:
        __simple_df_plot(df)

    parameters = {
        "alpha": alpha,
        "cut": cut,
        "trend": trend,
        "iterations": iterations,
        "feature_columns": [f"value-{i}" for i in range(len(alpha))],
        "channels": len(alpha),
        "anomalies": [{"kinds": [{"kind": "disconnect"}]}]
    }
    channel_anomalies = len(cut) - cut.count(None)
    alpha_list = alpha_t.flatten()
    influence = np.nanmean(np.where(alpha_list != 0, alpha_list, np.nan))
    if np.any(np.where(np.array(trend) == 0, False, True)):
        trend_info = f"{np.mean(trend)}_inclTrend"
    else:
        trend_info = "noTrend"

    if anomaly:
        anomaly_info = f"-{channel_anomalies}_channel_anomaly"
    else:
        anomaly_info = ""

    return df, parameters, f"{parameters['channels']}-corr-{influence}_mInfluence-{trend_info}{anomaly_info}"


def generate_correlation_2_data(alpha=None, cut=None, trend=None, iterations=100, anomaly=True, plot=False):
    if alpha is None:
        alpha = [[0, 0.5], [0, 0]]
    if cut is None:
        cut = [None, [50, 60]]
    return generate_correlation_data(alpha, cut, trend, iterations, anomaly, plot)


def generate_correlation_2_trend_data(alpha=None, cut=None, trend=None, iterations=100, anomaly=True, plot=False):
    if trend is None:
        trend = [2, -1]
    return generate_correlation_2_data(alpha, cut, trend, iterations, anomaly, plot)


def generate_correlation_2_trend_strong_data(alpha=None, cut=None, trend=None, iterations=100, anomaly=True,
                                             plot=False):
    if trend is None:
        trend = [2, -2]
    return generate_correlation_2_data(alpha, cut, trend, iterations, anomaly, plot)


def generate_correlation_2_high_corr_data(alpha=None, cut=None, trend=None, iterations=100, anomaly=True, plot=False):
    if alpha is None:
        alpha = [[0, 0.8], [0, 0]]
    if cut is None:
        cut = [None, [50, 60]]
    return generate_correlation_data(alpha, cut, trend, iterations, anomaly, plot)
