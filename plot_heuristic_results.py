# plot_heuristic_results.py
# ============================================================
# Plot JSSP Heuristic Benchmark Results
# ============================================================

import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_DIR
    / "heuristic_summary.csv"
)

GAP_OUTPUT_FILE = (
    PROJECT_DIR
    / "heuristic_gap_comparison.png"
)

WIN_OUTPUT_FILE = (
    PROJECT_DIR
    / "heuristic_win_rate.png"
)


RULES = [
    "SPT",
    "LPT",
    "MWKR",
]


# ============================================================
# 1. 读取 Summary
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
                    "rule": row["rule"],
                    "num_instances": int(
                        row["num_instances"]
                    ),
                    "best_or_tied_count": int(
                        row[
                            "best_or_tied_count"
                        ]
                    ),
                    "mean_gap": (
                        float(row["mean_gap"])
                        if row["mean_gap"]
                        else None
                    ),
                    "median_gap": (
                        float(row["median_gap"])
                        if row["median_gap"]
                        else None
                    ),
                    "median_runtime": float(
                        row["median_runtime"]
                    ),
                }
            )

    return results


# ============================================================
# 2. 整理不同规模
# ============================================================

def get_sizes(results):

    sizes = sorted(
        {
            (
                result["num_jobs"],
                result["num_machines"],
            )
            for result in results
        }
    )

    return sizes


# ============================================================
# 3. Gap Comparison
# ============================================================

def plot_gap_comparison(results):

    sizes = get_sizes(results)

    size_labels = [
        f"{jobs}x{machines}"
        for jobs, machines in sizes
    ]

    x = list(
        range(len(sizes))
    )

    width = 0.24


    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )


    for rule_index, rule in enumerate(
        RULES
    ):

        mean_gaps = []

        for (
            num_jobs,
            num_machines,
        ) in sizes:

            matching = [
                result
                for result in results
                if (
                    result["num_jobs"]
                    == num_jobs
                    and
                    result[
                        "num_machines"
                    ]
                    == num_machines
                    and
                    result["rule"]
                    == rule
                )
            ]

            result = matching[0]

            mean_gaps.append(
                100
                * result["mean_gap"]
            )


        positions = [
            value
            + (
                rule_index - 1
            ) * width
            for value in x
        ]


        ax.bar(
            positions,
            mean_gaps,
            width=width,
            label=rule,
        )


    ax.set_xlabel(
        "Problem Size"
    )

    ax.set_ylabel(
        "Mean Heuristic Gap (%)"
    )

    ax.set_title(
        "JSSP Heuristic Gap Comparison"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        size_labels
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4,
    )

    ax.legend()

    plt.tight_layout()


    plt.savefig(
        GAP_OUTPUT_FILE,
        dpi=200,
        bbox_inches="tight",
    )


    print(
        f"Gap comparison 已保存："
        f"{GAP_OUTPUT_FILE}"
    )

    plt.show()


# ============================================================
# 4. Best / Tied Rate
# ============================================================

def plot_win_rate(results):

    sizes = get_sizes(results)

    size_labels = [
        f"{jobs}x{machines}"
        for jobs, machines in sizes
    ]

    x = list(
        range(len(sizes))
    )

    width = 0.24


    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )


    for rule_index, rule in enumerate(
        RULES
    ):

        win_rates = []

        for (
            num_jobs,
            num_machines,
        ) in sizes:

            matching = [
                result
                for result in results
                if (
                    result["num_jobs"]
                    == num_jobs
                    and
                    result[
                        "num_machines"
                    ]
                    == num_machines
                    and
                    result["rule"]
                    == rule
                )
            ]

            result = matching[0]

            rate = (
                result[
                    "best_or_tied_count"
                ]
                /
                result[
                    "num_instances"
                ]
            )

            win_rates.append(
                100 * rate
            )


        positions = [
            value
            + (
                rule_index - 1
            ) * width
            for value in x
        ]


        ax.bar(
            positions,
            win_rates,
            width=width,
            label=rule,
        )


    ax.set_xlabel(
        "Problem Size"
    )

    ax.set_ylabel(
        "Best / Tied Rate (%)"
    )

    ax.set_title(
        "JSSP Heuristic Best-or-Tied Rate"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        size_labels
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4,
    )

    ax.legend()

    plt.tight_layout()


    plt.savefig(
        WIN_OUTPUT_FILE,
        dpi=200,
        bbox_inches="tight",
    )


    print(
        f"Win-rate plot 已保存："
        f"{WIN_OUTPUT_FILE}"
    )

    plt.show()


# ============================================================
# 5. Main
# ============================================================

def main():

    results = load_results(
        INPUT_FILE
    )

    plot_gap_comparison(
        results
    )

    plot_win_rate(
        results
    )


if __name__ == "__main__":

    main()