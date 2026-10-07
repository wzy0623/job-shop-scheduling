# plot_convergence.py
# ============================================================
# Plot JSSP Gurobi Convergence Results
# ============================================================

import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_DIR
    / "convergence_results.csv"
)

OUTPUT_BOUND_FILE = (
    PROJECT_DIR
    / "bound_convergence.png"
)

OUTPUT_GAP_FILE = (
    PROJECT_DIR
    / "gap_convergence.png"
)


# ============================================================
# 1. 读取结果
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

            incumbent = row["incumbent"]
            best_bound = row["best_bound"]
            mip_gap = row["mip_gap"]

            results.append(
                {
                    "time_limit": float(
                        row["time_limit"]
                    ),
                    "runtime": float(
                        row["runtime"]
                    ),
                    "status": row["status"],
                    "incumbent": (
                        float(incumbent)
                        if incumbent
                        else None
                    ),
                    "best_bound": (
                        float(best_bound)
                        if best_bound
                        else None
                    ),
                    "mip_gap": (
                        float(mip_gap)
                        if mip_gap
                        else None
                    ),
                }
            )

    return results


# ============================================================
# 2. Upper Bound / Lower Bound 图
# ============================================================

def plot_bound_convergence(results):

    times = []
    incumbents = []
    bounds = []

    for result in results:

        if (
            result["incumbent"] is None
            or result["best_bound"] is None
        ):
            continue

        times.append(
            result["time_limit"]
        )

        incumbents.append(
            result["incumbent"]
        )

        bounds.append(
            result["best_bound"]
        )


    fig, ax = plt.subplots(
        figsize=(8, 5.5)
    )


    ax.plot(
        times,
        incumbents,
        marker="o",
        label="Incumbent (Upper Bound)",
    )

    ax.plot(
        times,
        bounds,
        marker="s",
        label="Best Bound (Lower Bound)",
    )


    ax.set_xlabel(
        "Time Limit (seconds)"
    )

    ax.set_ylabel(
        "Makespan Bound"
    )

    ax.set_title(
        "JSSP Bound Convergence"
    )

    ax.set_xticks(times)

    ax.grid(
        linestyle="--",
        alpha=0.4,
    )

    ax.legend()

    plt.tight_layout()

    plt.savefig(
        OUTPUT_BOUND_FILE,
        dpi=200,
        bbox_inches="tight",
    )

    print(
        f"Bound convergence plot 已保存："
        f"{OUTPUT_BOUND_FILE}"
    )

    plt.show()


# ============================================================
# 3. MIP Gap 图
# ============================================================

def plot_gap_convergence(results):

    times = []
    gaps = []

    for result in results:

        if result["mip_gap"] is None:
            continue

        times.append(
            result["time_limit"]
        )

        gaps.append(
            100 * result["mip_gap"]
        )


    fig, ax = plt.subplots(
        figsize=(8, 5.5)
    )


    ax.plot(
        times,
        gaps,
        marker="o",
    )


    ax.set_xlabel(
        "Time Limit (seconds)"
    )

    ax.set_ylabel(
        "MIP Gap (%)"
    )

    ax.set_title(
        "JSSP Optimality Gap Convergence"
    )

    ax.set_xticks(times)

    ax.grid(
        linestyle="--",
        alpha=0.4,
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_GAP_FILE,
        dpi=200,
        bbox_inches="tight",
    )

    print(
        f"Gap convergence plot 已保存："
        f"{OUTPUT_GAP_FILE}"
    )

    plt.show()


# ============================================================
# 4. Main
# ============================================================

def main():

    results = load_results(
        INPUT_FILE
    )

    plot_bound_convergence(
        results
    )

    plot_gap_convergence(
        results
    )


if __name__ == "__main__":

    main()