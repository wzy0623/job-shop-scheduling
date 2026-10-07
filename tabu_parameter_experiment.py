# tabu_parameter_experiment.py
# ============================================================
# JSSP Tabu Search Parameter Experiment
#
# Study:
#   tabu tenure
#   max iterations
# ============================================================

import csv
import statistics
from pathlib import Path

from random_instance import (
    generate_random_instance,
)

from heuristic_solver import (
    solve_with_dispatching_rule,
)

from local_search import (
    improve_with_adjacent_swaps,
)

from tabu_search import (
    tabu_search,
)

from gurobi_solver import (
    solve_job_shop,
)


PROJECT_DIR = Path(__file__).resolve().parent


# ============================================================
# 1. Experiment Settings
# ============================================================

NUM_JOBS = 10
NUM_MACHINES = 10

SEEDS = list(range(10))

TABU_TENURES = [
    3,
    7,
    12,
]

MAX_ITERATIONS_LIST = [
    25,
    50,
    100,
]

GUROBI_TIME_LIMIT = 30


# ============================================================
# 2. Prepare Instances
# ============================================================

def prepare_instances():

    instances = []


    for seed in SEEDS:

        jobs, machines, big_m = (
            generate_random_instance(
                num_jobs=NUM_JOBS,
                num_machines=NUM_MACHINES,
                processing_time_min=1,
                processing_time_max=10,
                seed=seed,
            )
        )


        # ----------------------------------------------------
        # MWKR
        # ----------------------------------------------------

        (
            mwkr_start_times,
            mwkr_cmax,
            mwkr_stats,
        ) = solve_with_dispatching_rule(
            jobs=jobs,
            machines=machines,
            rule="MWKR",
        )


        # ----------------------------------------------------
        # Local Search
        # ----------------------------------------------------

        (
            local_start_times,
            local_cmax,
            local_stats,
        ) = improve_with_adjacent_swaps(
            jobs=jobs,
            machines=machines,
            initial_start_times=(
                mwkr_start_times
            ),
            max_iterations=100,
        )


        # ----------------------------------------------------
        # Gurobi Optimal Reference
        # ----------------------------------------------------

        (
            optimal_start_times,
            optimal_cmax,
            gurobi_stats,
        ) = solve_job_shop(
            jobs=jobs,
            machines=machines,
            big_m=big_m,
            verbose=False,
            return_stats=True,
            time_limit=GUROBI_TIME_LIMIT,
        )


        if (
            optimal_start_times is None
            or
            gurobi_stats["status"]
            != "OPTIMAL"
        ):

            print(
                f"seed={seed}: "
                f"Gurobi 未证明最优，跳过。"
            )

            continue


        instances.append(
            {
                "seed": seed,
                "jobs": jobs,
                "machines": machines,
                "local_start_times": (
                    local_start_times
                ),
                "local_cmax": (
                    local_cmax
                ),
                "optimal_cmax": (
                    optimal_cmax
                ),
            }
        )


    return instances


# ============================================================
# 3. Run One Parameter Combination
# ============================================================

def evaluate_parameters(
    instances,
    tabu_tenure,
    max_iterations,
):

    gaps = []

    runtimes = []

    improvements = []


    for instance in instances:

        (
            tabu_start_times,
            tabu_cmax,
            tabu_stats,
        ) = tabu_search(
            jobs=instance["jobs"],
            machines=instance[
                "machines"
            ],
            initial_start_times=(
                instance[
                    "local_start_times"
                ]
            ),
            max_iterations=(
                max_iterations
            ),
            tabu_tenure=(
                tabu_tenure
            ),
        )


        gap = (
            (
                tabu_cmax
                - instance[
                    "optimal_cmax"
                ]
            )
            / instance[
                "optimal_cmax"
            ]
        )


        improvement = (
            (
                instance[
                    "local_cmax"
                ]
                - tabu_cmax
            )
            / instance[
                "local_cmax"
            ]
        )


        gaps.append(
            gap
        )

        runtimes.append(
            tabu_stats["runtime"]
        )

        improvements.append(
            improvement
        )


    return {
        "tabu_tenure": (
            tabu_tenure
        ),
        "max_iterations": (
            max_iterations
        ),
        "num_instances": (
            len(instances)
        ),
        "mean_gap": (
            statistics.mean(gaps)
        ),
        "median_gap": (
            statistics.median(gaps)
        ),
        "mean_improvement": (
            statistics.mean(
                improvements
            )
        ),
        "median_runtime": (
            statistics.median(
                runtimes
            )
        ),
        "mean_runtime": (
            statistics.mean(
                runtimes
            )
        ),
    }


# ============================================================
# 4. Save Results
# ============================================================

def save_results(
    results,
    filename,
):

    fieldnames = list(
        results[0].keys()
    )


    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            results
        )


# ============================================================
# 5. Main
# ============================================================

def main():

    print("=" * 100)

    print(
        "JSSP Tabu Search "
        "Parameter Experiment"
    )

    print("=" * 100)


    # ========================================================
    # Prepare the same instances once
    # ========================================================

    instances = (
        prepare_instances()
    )


    print(
        f"\nUsable instances: "
        f"{len(instances)}"
    )


    results = []


    # ========================================================
    # Parameter Grid
    # ========================================================

    for tabu_tenure in TABU_TENURES:

        for max_iterations in (
            MAX_ITERATIONS_LIST
        ):

            print(
                f"\nTesting tenure="
                f"{tabu_tenure}, "
                f"iterations="
                f"{max_iterations}"
            )


            result = (
                evaluate_parameters(
                    instances=instances,
                    tabu_tenure=(
                        tabu_tenure
                    ),
                    max_iterations=(
                        max_iterations
                    ),
                )
            )


            results.append(
                result
            )


            print(
                f"  Mean Gap = "
                f"{100 * result['mean_gap']:.2f}%"
            )

            print(
                f"  Median Gap = "
                f"{100 * result['median_gap']:.2f}%"
            )

            print(
                f"  Improvement = "
                f"{100 * result['mean_improvement']:.2f}%"
            )

            print(
                f"  Median Runtime = "
                f"{1000 * result['median_runtime']:.2f} ms"
            )


    # ========================================================
    # Summary
    # ========================================================

    print(
        "\n" + "=" * 110
    )

    print(
        "Summary"
    )

    print(
        "=" * 110
    )


    print(
        f"{'Tenure':<10}"
        f"{'Iter':<10}"
        f"{'MeanGap%':<14}"
        f"{'MedianGap%':<14}"
        f"{'Improve%':<14}"
        f"{'Runtime(ms)':<14}"
    )

    print(
        "-" * 110
    )


    for result in results:

        print(
            f"{result['tabu_tenure']:<10}"
            f"{result['max_iterations']:<10}"
            f"{100 * result['mean_gap']:<14.2f}"
            f"{100 * result['median_gap']:<14.2f}"
            f"{100 * result['mean_improvement']:<14.2f}"
            f"{1000 * result['median_runtime']:<14.2f}"
        )


    # ========================================================
    # Best Mean Gap
    # ========================================================

    best_quality = min(
        results,
        key=lambda result: (
            result["mean_gap"]
        ),
    )


    print(
        "\nBest solution quality:"
    )

    print(
        f"  tenure = "
        f"{best_quality['tabu_tenure']}"
    )

    print(
        f"  iterations = "
        f"{best_quality['max_iterations']}"
    )

    print(
        f"  mean gap = "
        f"{100 * best_quality['mean_gap']:.2f}%"
    )

    print(
        f"  median runtime = "
        f"{1000 * best_quality['median_runtime']:.2f} ms"
    )


    # ========================================================
    # Save
    # ========================================================

    output_file = (
        PROJECT_DIR
        / "tabu_parameter_results.csv"
    )


    save_results(
        results,
        output_file,
    )


    print(
        "\n结果已保存："
        f"{output_file}"
    )


if __name__ == "__main__":

    main()