# tabu_benchmark.py
# ============================================================
# JSSP Benchmark
#
# MWKR
# -> Local Search
# -> Tabu Search
# -> Gurobi Optimal Reference
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

from validator import (
    check_job_precedence,
    check_machine_non_overlap,
    check_makespan,
)


PROJECT_DIR = Path(__file__).resolve().parent


# ============================================================
# 1. Experiment Settings
# ============================================================

NUM_JOBS = 10
NUM_MACHINES = 10

SEEDS = list(range(20))

GUROBI_TIME_LIMIT = 30

LOCAL_MAX_ITERATIONS = 100

TABU_MAX_ITERATIONS = 100

TABU_TENURE = 7


# ============================================================
# 2. Silent Validator
# ============================================================

def is_valid_schedule(
    jobs,
    machines,
    start_times,
    cmax_value,
):

    precedence_ok = (
        check_job_precedence(
            jobs,
            start_times,
        )
    )

    machine_ok = (
        check_machine_non_overlap(
            jobs,
            machines,
            start_times,
        )
    )

    makespan_ok = (
        check_makespan(
            jobs,
            start_times,
            cmax_value,
        )
    )

    return (
        precedence_ok
        and machine_ok
        and makespan_ok
    )


# ============================================================
# 3. Run One Instance
# ============================================================

def run_single_instance(seed):

    # ========================================================
    # Generate Instance
    # ========================================================

    jobs, machines, big_m = (
        generate_random_instance(
            num_jobs=NUM_JOBS,
            num_machines=NUM_MACHINES,
            processing_time_min=1,
            processing_time_max=10,
            seed=seed,
        )
    )


    # ========================================================
    # MWKR
    # ========================================================

    (
        mwkr_start_times,
        mwkr_cmax,
        mwkr_stats,
    ) = solve_with_dispatching_rule(
        jobs=jobs,
        machines=machines,
        rule="MWKR",
    )


    # ========================================================
    # Local Search
    # ========================================================

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
        max_iterations=(
            LOCAL_MAX_ITERATIONS
        ),
    )


    # ========================================================
    # Tabu Search
    #
    # 注意：
    #
    # Tabu 从 Local Search 的局部最优解出发。
    # ========================================================

    (
        tabu_start_times,
        tabu_cmax,
        tabu_stats,
    ) = tabu_search(
        jobs=jobs,
        machines=machines,
        initial_start_times=(
            local_start_times
        ),
        max_iterations=(
            TABU_MAX_ITERATIONS
        ),
        tabu_tenure=(
            TABU_TENURE
        ),
    )


    # ========================================================
    # Validation
    # ========================================================

    local_valid = is_valid_schedule(
        jobs=jobs,
        machines=machines,
        start_times=local_start_times,
        cmax_value=local_cmax,
    )

    tabu_valid = is_valid_schedule(
        jobs=jobs,
        machines=machines,
        start_times=tabu_start_times,
        cmax_value=tabu_cmax,
    )


    # ========================================================
    # Gurobi
    # ========================================================

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


    gurobi_optimal = (
        optimal_start_times is not None
        and
        gurobi_stats["status"]
        == "OPTIMAL"
    )


    # ========================================================
    # Gaps
    # ========================================================

    if gurobi_optimal:

        mwkr_gap = (
            (
                mwkr_cmax
                - optimal_cmax
            )
            / optimal_cmax
        )

        local_gap = (
            (
                local_cmax
                - optimal_cmax
            )
            / optimal_cmax
        )

        tabu_gap = (
            (
                tabu_cmax
                - optimal_cmax
            )
            / optimal_cmax
        )

    else:

        mwkr_gap = None
        local_gap = None
        tabu_gap = None


    # ========================================================
    # Tabu Improvement over Local
    # ========================================================

    tabu_improvement = (
        (
            local_cmax
            - tabu_cmax
        )
        / local_cmax
    )


    return {
        "seed": seed,

        "gurobi_status": (
            gurobi_stats["status"]
        ),

        "optimal_cmax": (
            optimal_cmax
            if gurobi_optimal
            else None
        ),

        "mwkr_cmax": mwkr_cmax,

        "local_cmax": local_cmax,

        "tabu_cmax": tabu_cmax,

        "mwkr_gap": mwkr_gap,

        "local_gap": local_gap,

        "tabu_gap": tabu_gap,

        "tabu_improvement": (
            tabu_improvement
        ),

        "mwkr_runtime": (
            mwkr_stats["runtime"]
        ),

        "local_runtime": (
            local_stats["runtime"]
        ),

        "tabu_runtime": (
            tabu_stats["runtime"]
        ),

        "gurobi_runtime": (
            gurobi_stats["runtime"]
        ),

        "local_valid": (
            local_valid
        ),

        "tabu_valid": (
            tabu_valid
        ),

        "tabu_iterations": (
            tabu_stats["iterations"]
        ),

        "accepted_worsening_moves": (
            tabu_stats[
                "accepted_worsening_moves"
            ]
        ),

        "accepted_equal_moves": (
            tabu_stats[
                "accepted_equal_moves"
            ]
        ),

        "best_improvements": (
            tabu_stats[
                "best_improvements"
            ]
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

    results = []


    print("=" * 110)

    print(
        "JSSP Local Search vs Tabu Search Benchmark"
    )

    print(
        f"Instance size: "
        f"{NUM_JOBS}x{NUM_MACHINES}"
    )

    print(
        f"Number of instances: "
        f"{len(SEEDS)}"
    )

    print("=" * 110)


    # ========================================================
    # Run Instances
    # ========================================================

    for seed in SEEDS:

        result = (
            run_single_instance(
                seed
            )
        )

        results.append(
            result
        )


        print(
            f"seed={seed:<2} | "
            f"MWKR={result['mwkr_cmax']:<5.0f} | "
            f"Local={result['local_cmax']:<5.0f} | "
            f"Tabu={result['tabu_cmax']:<5.0f} | "
            f"Tabu Improve="
            f"{100 * result['tabu_improvement']:.2f}%"
        )


    # ========================================================
    # Statistics
    # ========================================================

    optimal_results = [
        result
        for result in results
        if result["gurobi_status"]
        == "OPTIMAL"
    ]


    mwkr_gaps = [
        result["mwkr_gap"]
        for result in optimal_results
    ]

    local_gaps = [
        result["local_gap"]
        for result in optimal_results
    ]

    tabu_gaps = [
        result["tabu_gap"]
        for result in optimal_results
    ]


    tabu_improvements = [
        result["tabu_improvement"]
        for result in results
    ]


    tabu_better_count = sum(
        result["tabu_cmax"]
        < result["local_cmax"]
        - 1e-9
        for result in results
    )


    tabu_equal_count = sum(
        abs(
            result["tabu_cmax"]
            - result["local_cmax"]
        )
        <= 1e-9
        for result in results
    )


    local_valid_count = sum(
        result["local_valid"]
        for result in results
    )

    tabu_valid_count = sum(
        result["tabu_valid"]
        for result in results
    )


    # ========================================================
    # Runtime
    # ========================================================

    local_runtimes = [
        result["local_runtime"]
        for result in results
    ]

    tabu_runtimes = [
        result["tabu_runtime"]
        for result in results
    ]

    gurobi_runtimes = [
        result["gurobi_runtime"]
        for result in results
    ]


    # ========================================================
    # Print Summary
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
        f"Gurobi optimal instances: "
        f"{len(optimal_results)}/{len(results)}"
    )

    print(
        f"Local valid: "
        f"{local_valid_count}/{len(results)}"
    )

    print(
        f"Tabu valid: "
        f"{tabu_valid_count}/{len(results)}"
    )


    print()


    if optimal_results:

        print(
            "Mean Gap to Optimal"
        )

        print(
            f"  MWKR:  "
            f"{100 * statistics.mean(mwkr_gaps):.2f}%"
        )

        print(
            f"  Local: "
            f"{100 * statistics.mean(local_gaps):.2f}%"
        )

        print(
            f"  Tabu:  "
            f"{100 * statistics.mean(tabu_gaps):.2f}%"
        )


        print()


        print(
            "Median Gap to Optimal"
        )

        print(
            f"  MWKR:  "
            f"{100 * statistics.median(mwkr_gaps):.2f}%"
        )

        print(
            f"  Local: "
            f"{100 * statistics.median(local_gaps):.2f}%"
        )

        print(
            f"  Tabu:  "
            f"{100 * statistics.median(tabu_gaps):.2f}%"
        )


    print()


    print(
        f"Tabu strictly better than Local: "
        f"{tabu_better_count}/{len(results)}"
    )

    print(
        f"Tabu equal to Local: "
        f"{tabu_equal_count}/{len(results)}"
    )

    print(
        f"Mean Tabu improvement over Local: "
        f"{100 * statistics.mean(tabu_improvements):.2f}%"
    )

    print(
        f"Median Tabu improvement over Local: "
        f"{100 * statistics.median(tabu_improvements):.2f}%"
    )


    print()


    print(
        "Median Runtime"
    )

    print(
        f"  Local Search: "
        f"{1000 * statistics.median(local_runtimes):.2f} ms"
    )

    print(
        f"  Tabu Search:  "
        f"{1000 * statistics.median(tabu_runtimes):.2f} ms"
    )

    print(
        f"  Gurobi:       "
        f"{1000 * statistics.median(gurobi_runtimes):.2f} ms"
    )


    # ========================================================
    # Save
    # ========================================================

    output_file = (
        PROJECT_DIR
        / "tabu_benchmark_results.csv"
    )


    save_results(
        results,
        output_file,
    )


    print(
        "\n" + "=" * 110
    )

    print(
        f"结果已保存："
        f"{output_file}"
    )


if __name__ == "__main__":

    main()