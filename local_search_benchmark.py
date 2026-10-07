# local_search_benchmark.py
# ============================================================
# Job Shop Scheduling
# MWKR vs MWKR + Local Search Benchmark
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

SIZES = [
    (5, 5),
    (7, 7),
    (10, 10),
]

SEEDS = list(range(20))

GUROBI_TIME_LIMIT = 30

MAX_LOCAL_SEARCH_ITERATIONS = 100


# ============================================================
# 2. Silent Validator
# ============================================================

def is_valid_schedule(
    jobs,
    machines,
    start_times,
    cmax_value,
):
    precedence_ok = check_job_precedence(
        jobs,
        start_times,
    )

    machine_ok = check_machine_non_overlap(
        jobs,
        machines,
        start_times,
    )

    makespan_ok = check_makespan(
        jobs,
        start_times,
        cmax_value,
    )

    return (
        precedence_ok
        and machine_ok
        and makespan_ok
    )


# ============================================================
# 3. Run One Instance
# ============================================================

def run_single_instance(
    num_jobs,
    num_machines,
    seed,
):
    # --------------------------------------------------------
    # Generate instance
    # --------------------------------------------------------

    jobs, machines, big_m = (
        generate_random_instance(
            num_jobs=num_jobs,
            num_machines=num_machines,
            processing_time_min=1,
            processing_time_max=10,
            seed=seed,
        )
    )


    # ========================================================
    # 4. MWKR
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


    mwkr_valid = is_valid_schedule(
        jobs=jobs,
        machines=machines,
        start_times=mwkr_start_times,
        cmax_value=mwkr_cmax,
    )


    # ========================================================
    # 5. Local Search
    # ========================================================

    (
        local_start_times,
        local_cmax,
        local_stats,
    ) = improve_with_adjacent_swaps(
        jobs=jobs,
        machines=machines,
        initial_start_times=mwkr_start_times,
        max_iterations=(
            MAX_LOCAL_SEARCH_ITERATIONS
        ),
    )


    local_valid = is_valid_schedule(
        jobs=jobs,
        machines=machines,
        start_times=local_start_times,
        cmax_value=local_cmax,
    )


    decoded_initial_cmax = (
        local_stats[
            "decoded_initial_cmax"
        ]
    )


    # ========================================================
    # 6. Improvement Metrics
    # ========================================================

    compression_improvement = (
        (
            mwkr_cmax
            - decoded_initial_cmax
        )
        / mwkr_cmax
    )


    swap_improvement = (
        (
            decoded_initial_cmax
            - local_cmax
        )
        / decoded_initial_cmax
    )


    total_improvement = (
        (
            mwkr_cmax
            - local_cmax
        )
        / mwkr_cmax
    )


    # ========================================================
    # 7. Gurobi Optimal Reference
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

    else:

        mwkr_gap = None
        local_gap = None


    # ========================================================
    # 8. Return Result
    # ========================================================

    return {
        "num_jobs": num_jobs,
        "num_machines": num_machines,
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

        "decoded_initial_cmax": (
            decoded_initial_cmax
        ),

        "local_cmax": local_cmax,

        "mwkr_gap": mwkr_gap,
        "local_gap": local_gap,

        "compression_improvement": (
            compression_improvement
        ),

        "swap_improvement": (
            swap_improvement
        ),

        "total_improvement": (
            total_improvement
        ),

        "mwkr_runtime": (
            mwkr_stats["runtime"]
        ),

        "local_runtime": (
            local_stats["runtime"]
        ),

        "local_iterations": (
            local_stats["iterations"]
        ),

        "evaluated_moves": (
            local_stats[
                "evaluated_moves"
            ]
        ),

        "feasible_moves": (
            local_stats[
                "feasible_moves"
            ]
        ),

        "mwkr_valid": mwkr_valid,
        "local_valid": local_valid,
    }


# ============================================================
# 9. Build Summary
# ============================================================

def build_summary(
    all_results,
):
    summary = []


    for (
        num_jobs,
        num_machines,
    ) in SIZES:

        results = [
            result
            for result in all_results
            if (
                result["num_jobs"]
                == num_jobs
                and
                result["num_machines"]
                == num_machines
            )
        ]


        mwkr_gaps = [
            result["mwkr_gap"]
            for result in results
            if result["mwkr_gap"]
            is not None
        ]


        local_gaps = [
            result["local_gap"]
            for result in results
            if result["local_gap"]
            is not None
        ]


        compression_improvements = [
            result[
                "compression_improvement"
            ]
            for result in results
        ]


        swap_improvements = [
            result[
                "swap_improvement"
            ]
            for result in results
        ]


        total_improvements = [
            result[
                "total_improvement"
            ]
            for result in results
        ]


        mwkr_runtimes = [
            result["mwkr_runtime"]
            for result in results
        ]


        local_runtimes = [
            result["local_runtime"]
            for result in results
        ]


        improved_count = sum(
            result["local_cmax"]
            < result["mwkr_cmax"]
            - 1e-9
            for result in results
        )


        equal_count = sum(
            abs(
                result["local_cmax"]
                - result["mwkr_cmax"]
            )
            <= 1e-9
            for result in results
        )


        valid_count = sum(
            result["local_valid"]
            for result in results
        )


        optimal_count = sum(
            result["gurobi_status"]
            == "OPTIMAL"
            for result in results
        )


        row = {
            "num_jobs": num_jobs,
            "num_machines": num_machines,
            "num_instances": len(results),
            "optimal_count": optimal_count,
            "valid_count": valid_count,
            "improved_count": (
                improved_count
            ),
            "equal_count": (
                equal_count
            ),

            "mean_compression_improvement": (
                statistics.mean(
                    compression_improvements
                )
            ),

            "mean_swap_improvement": (
                statistics.mean(
                    swap_improvements
                )
            ),

            "mean_total_improvement": (
                statistics.mean(
                    total_improvements
                )
            ),

            "median_total_improvement": (
                statistics.median(
                    total_improvements
                )
            ),

            "median_mwkr_runtime": (
                statistics.median(
                    mwkr_runtimes
                )
            ),

            "median_local_runtime": (
                statistics.median(
                    local_runtimes
                )
            ),

            "mean_mwkr_gap": (
                statistics.mean(
                    mwkr_gaps
                )
                if mwkr_gaps
                else None
            ),

            "mean_local_gap": (
                statistics.mean(
                    local_gaps
                )
                if local_gaps
                else None
            ),

            "median_mwkr_gap": (
                statistics.median(
                    mwkr_gaps
                )
                if mwkr_gaps
                else None
            ),

            "median_local_gap": (
                statistics.median(
                    local_gaps
                )
                if local_gaps
                else None
            ),
        }


        summary.append(row)


    return summary


# ============================================================
# 10. Save Instance Results
# ============================================================

def save_instance_results(
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

        writer.writerows(results)


# ============================================================
# 11. Save Summary
# ============================================================

def save_summary(
    summary,
    filename,
):
    fieldnames = list(
        summary[0].keys()
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

        writer.writerows(summary)


# ============================================================
# 12. Main
# ============================================================

def main():

    all_results = []


    print("=" * 110)

    print(
        "MWKR + Local Search Benchmark"
    )

    print("=" * 110)


    for (
        num_jobs,
        num_machines,
    ) in SIZES:

        print(
            "\n" + "-" * 110
        )

        print(
            f"Testing "
            f"{num_jobs}x{num_machines}"
        )

        print(
            "-" * 110
        )


        for seed in SEEDS:

            result = run_single_instance(
                num_jobs=num_jobs,
                num_machines=num_machines,
                seed=seed,
            )


            all_results.append(
                result
            )


            print(
                f"seed={seed:<2} | "
                f"MWKR="
                f"{result['mwkr_cmax']:<6.0f} | "
                f"Decoded="
                f"{result['decoded_initial_cmax']:<6.0f} | "
                f"Local="
                f"{result['local_cmax']:<6.0f} | "
                f"Improve="
                f"{100 * result['total_improvement']:.2f}%"
            )


    # ========================================================
    # Summary
    # ========================================================

    summary = build_summary(
        all_results
    )


    print(
        "\n" + "=" * 120
    )

    print(
        "Summary"
    )

    print(
        "=" * 120
    )


    print(
        f"{'Size':<10}"
        f"{'Improved':<12}"
        f"{'TotalImp%':<14}"
        f"{'MWKRGap%':<14}"
        f"{'LocalGap%':<14}"
        f"{'MWKRms':<12}"
        f"{'Localms':<12}"
        f"{'Valid':<10}"
    )

    print(
        "-" * 120
    )


    for row in summary:

        size_text = (
            f"{row['num_jobs']}"
            f"x"
            f"{row['num_machines']}"
        )


        if row["mean_mwkr_gap"] is None:

            mwkr_gap_text = "-"
            local_gap_text = "-"

        else:

            mwkr_gap_text = (
                f"{100 * row['mean_mwkr_gap']:.2f}"
            )

            local_gap_text = (
                f"{100 * row['mean_local_gap']:.2f}"
            )


        improved_text = (
            f"{row['improved_count']}"
            f"/"
            f"{row['num_instances']}"
        )


        valid_text = (
            f"{row['valid_count']}"
            f"/"
            f"{row['num_instances']}"
        )


        print(
            f"{size_text:<10}"
            f"{improved_text:<12}"
            f"{100 * row['mean_total_improvement']:<14.2f}"
            f"{mwkr_gap_text:<14}"
            f"{local_gap_text:<14}"
            f"{1000 * row['median_mwkr_runtime']:<12.4f}"
            f"{1000 * row['median_local_runtime']:<12.4f}"
            f"{valid_text:<10}"
        )


    # ========================================================
    # Save Results
    # ========================================================

    instance_file = (
        PROJECT_DIR
        / "local_search_instance_results.csv"
    )

    summary_file = (
        PROJECT_DIR
        / "local_search_summary.csv"
    )


    save_instance_results(
        all_results,
        instance_file,
    )

    save_summary(
        summary,
        summary_file,
    )


    print(
        "\n" + "=" * 120
    )

    print(
        f"逐实例结果："
        f"{instance_file}"
    )

    print(
        f"汇总结果："
        f"{summary_file}"
    )

    print(
        f"总实例数量："
        f"{len(all_results)}"
    )


if __name__ == "__main__":

    main()