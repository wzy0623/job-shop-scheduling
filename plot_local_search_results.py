# plot_local_search_results.py
# ============================================================
# Plot MWKR + Local Search Benchmark Results
# ============================================================

import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_DIR
    / "local_search_summary.csv"
)

GAP_OUTPUT_FILE = (
    PROJECT_DIR
    / "local_search_gap_comparison.png"
)

IMPROVEMENT_OUTPUT_FILE = (
    PROJECT_DIR
    / "local_search_improvement_rate.png"
)


# ============================================================
# 1. Load Results
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
                    "num_instances": int(
                        row["num_instances"]
                    ),
                    "improved_count": int(
                        row["improved_count"]
                    ),
                    "mean_total_improvement": float(
                        row[
                            "mean_total_improvement"
                        ]
                    ),
                    "mean_mwkr_gap": float(
                        row["mean_mwkr_gap"]
                    ),
                    "mean_local_gap": float(
                        row["mean_local_gap"]
                    ),
                    "median_mwkr_runtime": float(
                        row[
                            "median_mwkr_runtime"
                        ]
                    ),
                    "median_local_runtime": float(
                        row[
                            "median_local_runtime"
                        ]
                    ),
                }
            )

    return results


# ============================================================
# 2. MWKR Gap vs Local Search Gap
# ============================================================

def plot_gap_comparison(results):

    size_labels = [
        (
            f"{result['num_jobs']}"
            f"x"
            f"{result['num_machines']}"
        )
        for result in results
    ]

    x = list(
        range(len(results))
    )

    width = 0.34


    mwkr_gaps = [
        100 * result["mean_mwkr_gap"]
        for result in results
    ]

    local_gaps = [
        100 * result["mean_local_gap"]
        for result in results
    ]


    fig, ax = plt.subplots(
        figsize=(8.5, 5.5)
    )


    mwkr_positions = [
        value - width / 2
        for value in x
    ]

    local_positions = [
        value + width / 2
        for value in x
    ]


    ax.bar(
        mwkr_positions,
        mwkr_gaps,
        width=width,
        label="MWKR",
    )

    ax.bar(
        local_positions,
        local_gaps,
        width=width,
        label="MWKR + Local Search",
    )


    ax.set_xlabel(
        "Problem Size"
    )

    ax.set_ylabel(
        "Mean Gap to Optimal (%)"
    )

    ax.set_title(
        "MWKR vs MWKR + Local Search"
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
# 3. Improvement Rate
# ============================================================

def plot_improvement_rate(results):

    size_labels = [
        (
            f"{result['num_jobs']}"
            f"x"
            f"{result['num_machines']}"
        )
        for result in results
    ]


    improvement_rates = [
        (
            result["improved_count"]
            /
            result["num_instances"]
            * 100
        )
        for result in results
    ]


    fig, ax = plt.subplots(
        figsize=(8.5, 5.5)
    )


    bars = ax.bar(
        size_labels,
        improvement_rates,
    )


    ax.set_xlabel(
        "Problem Size"
    )

    ax.set_ylabel(
        "Instances Improved (%)"
    )

    ax.set_title(
        "Local Search Improvement Rate"
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


    # ========================================================
    # 在柱子上标数值
    # ========================================================

    for bar, rate in zip(
        bars,
        improvement_rates,
    ):

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{rate:.0f}%",
            ha="center",
            va="bottom",
        )


    plt.tight_layout()


    plt.savefig(
        IMPROVEMENT_OUTPUT_FILE,
        dpi=200,
        bbox_inches="tight",
    )


    print(
        f"Improvement-rate plot 已保存："
        f"{IMPROVEMENT_OUTPUT_FILE}"
    )

    plt.show()


# ============================================================
# 4. Main
# ============================================================

def main():

    results = load_results(
        INPUT_FILE
    )

    plot_gap_comparison(
        results
    )

    plot_improvement_rate(
        results
    )


if __name__ == "__main__":

    main()