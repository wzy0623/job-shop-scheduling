# plot_results.py
# ============================================================
# Plot JSSP Benchmark Results
# ============================================================

import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_DIR
    / "experiment_summary.csv"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "runtime_scaling.png"
)


# ============================================================
# 1. 读取实验结果
# ============================================================

def load_results(filename):

    results = []

    with open(
        filename,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            results.append(
                {
                    "num_jobs": int(
                        row["num_jobs"]
                    ),
                    "num_machines": int(
                        row["num_machines"]
                    ),
                    "mean_runtime": float(
                        row["mean_runtime"]
                    ),
                    "median_runtime": float(
                        row["median_runtime"]
                    ),
                    "std_runtime": float(
                        row["std_runtime"]
                    ),
                }
            )

    return results


# ============================================================
# 2. 绘图
# ============================================================

def plot_runtime(results):

    sizes = [
        result["num_jobs"]
        for result in results
    ]

    medians = [
        result["median_runtime"]
        for result in results
    ]

    means = [
        result["mean_runtime"]
        for result in results
    ]

    stds = [
        result["std_runtime"]
        for result in results
    ]


    fig, ax = plt.subplots(
        figsize=(8, 5.5)
    )


    # Median Runtime

    ax.plot(
        sizes,
        medians,
        marker="o",
        label="Median Runtime",
    )


    # Mean Runtime + Std

    ax.errorbar(
        sizes,
        means,
        yerr=stds,
        marker="s",
        capsize=4,
        label="Mean Runtime ± Std",
    )


    ax.set_xlabel(
        "Problem Size (n × n)"
    )

    ax.set_ylabel(
        "Gurobi Runtime (seconds)"
    )

    ax.set_title(
        "JSSP Runtime Scaling"
    )

    ax.set_xticks(sizes)

    ax.grid(
        linestyle="--",
        alpha=0.4,
    )

    ax.legend()

    plt.tight_layout()


    plt.savefig(
        OUTPUT_FILE,
        dpi=200,
        bbox_inches="tight",
    )


    print(
        f"Runtime plot 已保存："
        f"{OUTPUT_FILE}"
    )


    plt.show()


# ============================================================
# 3. Main
# ============================================================

def main():

    results = load_results(
        INPUT_FILE
    )

    plot_runtime(
        results
    )


if __name__ == "__main__":

    main()