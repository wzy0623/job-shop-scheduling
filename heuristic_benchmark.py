# heuristic_benchmark.py
# ============================================================
# Job Shop Scheduling
# Heuristic Benchmark:
# SPT vs LPT vs MWKR
# ============================================================

import csv
import statistics
from pathlib import Path

from random_instance import (
    generate_random_instance,
)

from gurobi_solver import (
    solve_job_shop,
)

from heuristic_solver import (
    solve_with_dispatching_rule,
)

from validator import (
    check_job_precedence,
    check_machine_non_overlap,
    check_makespan,
)


PROJECT_DIR = Path(__file__).resolve().parent


# ============================================================
# 1. 实验参数
# ============================================================

SIZES = [
    (5, 5),
    (7, 7),
    (10, 10),
]

SEEDS = list(range(20))

RULES = [
    "SPT",
    "LPT",
    "MWKR",
]

GUROBI_TIME_LIMIT = 30


# ============================================================
# 2. 不打印大段信息的 Validator
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
# 3. 单个随机实例
# ============================================================

def run_single_instance(
    num_jobs,
    num_machines,
    seed,
):
    # --------------------------------------------------------
    # 生成实例
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


    # --------------------------------------------------------
    # Gurobi
    # --------------------------------------------------------

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
        and gurobi_stats["status"]
        == "OPTIMAL"
    )


    # --------------------------------------------------------
    # 三种 Heuristic
    # --------------------------------------------------------

    heuristic_results = {}


    for rule in RULES:

        (
            start_times,
            cmax_value,
            heuristic_stats,
        ) = solve_with_dispatching_rule(
            jobs=jobs,
            machines=machines,
            rule=rule,
        )


        valid = is_valid_schedule(
            jobs=jobs,
            machines=machines,
            start_times=start_times,
            cmax_value=cmax_value,
        )


        # ----------------------------------------------------
        # 只有 Gurobi 已证明最优时，
        # 才计算真正的 Heuristic Gap。
        # ----------------------------------------------------

        if gurobi_optimal:

            gap = (
                (
                    cmax_value
                    - optimal_cmax
                )
                / optimal_cmax
            )

        else:

            gap = None


        heuristic_results[rule] = {
            "makespan": cmax_value,
            "runtime": (
                heuristic_stats["runtime"]
            ),
            "valid": valid,
            "gap": gap,
        }


    # ========================================================
    # 4. 找当前实例中最好的 Heuristic
    # ========================================================

    best_heuristic_makespan = min(
        result["makespan"]
        for result
        in heuristic_results.values()
    )


    for rule in RULES:

        heuristic_results[
            rule
        ]["best_or_tied"] = (
            heuristic_results[
                rule
            ]["makespan"]
            ==
            best_heuristic_makespan
        )


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
        "gurobi_runtime": (
            gurobi_stats["runtime"]
        ),
        "heuristics": (
            heuristic_results
        ),
    }


# ============================================================
# 5. 保存逐实例结果
# ============================================================

def save_instance_results(
    results,
    filename,
):
    fieldnames = [
        "num_jobs",
        "num_machines",
        "seed",
        "gurobi_status",
        "optimal_cmax",
        "gurobi_runtime",
        "rule",
        "heuristic_cmax",
        "heuristic_runtime",
        "gap",
        "valid",
        "best_or_tied",
    ]


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


        for result in results:

            for rule in RULES:

                h = result[
                    "heuristics"
                ][rule]

                writer.writerow(
                    {
                        "num_jobs": (
                            result[
                                "num_jobs"
                            ]
                        ),
                        "num_machines": (
                            result[
                                "num_machines"
                            ]
                        ),
                        "seed": (
                            result[
                                "seed"
                            ]
                        ),
                        "gurobi_status": (
                            result[
                                "gurobi_status"
                            ]
                        ),
                        "optimal_cmax": (
                            result[
                                "optimal_cmax"
                            ]
                        ),
                        "gurobi_runtime": (
                            result[
                                "gurobi_runtime"
                            ]
                        ),
                        "rule": rule,
                        "heuristic_cmax": (
                            h["makespan"]
                        ),
                        "heuristic_runtime": (
                            h["runtime"]
                        ),
                        "gap": (
                            h["gap"]
                        ),
                        "valid": (
                            h["valid"]
                        ),
                        "best_or_tied": (
                            h[
                                "best_or_tied"
                            ]
                        ),
                    }
                )


# ============================================================
# 6. 计算 Summary
# ============================================================

def build_summary(
    all_results,
):
    summary_rows = []


    for (
        num_jobs,
        num_machines,
    ) in SIZES:

        size_results = [
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


        optimal_instances = sum(
            result["gurobi_status"]
            == "OPTIMAL"
            for result in size_results
        )


        for rule in RULES:

            rule_results = [
                result["heuristics"][
                    rule
                ]
                for result
                in size_results
            ]


            runtimes = [
                result["runtime"]
                for result
                in rule_results
            ]


            makespans = [
                result["makespan"]
                for result
                in rule_results
            ]


            gaps = [
                result["gap"]
                for result
                in rule_results
                if result["gap"]
                is not None
            ]


            valid_count = sum(
                result["valid"]
                for result
                in rule_results
            )


            best_or_tied_count = sum(
                result["best_or_tied"]
                for result
                in rule_results
            )


            if gaps:

                mean_gap = (
                    statistics.mean(gaps)
                )

                median_gap = (
                    statistics.median(gaps)
                )

            else:

                mean_gap = None
                median_gap = None


            summary_rows.append(
                {
                    "num_jobs": (
                        num_jobs
                    ),
                    "num_machines": (
                        num_machines
                    ),
                    "rule": rule,
                    "num_instances": (
                        len(size_results)
                    ),
                    "optimal_instances": (
                        optimal_instances
                    ),
                    "valid_count": (
                        valid_count
                    ),
                    "best_or_tied_count": (
                        best_or_tied_count
                    ),
                    "mean_makespan": (
                        statistics.mean(
                            makespans
                        )
                    ),
                    "mean_gap": (
                        mean_gap
                    ),
                    "median_gap": (
                        median_gap
                    ),
                    "mean_runtime": (
                        statistics.mean(
                            runtimes
                        )
                    ),
                    "median_runtime": (
                        statistics.median(
                            runtimes
                        )
                    ),
                }
            )


    return summary_rows


# ============================================================
# 7. 保存 Summary
# ============================================================

def save_summary(
    summary_rows,
    filename,
):
    fieldnames = [
        "num_jobs",
        "num_machines",
        "rule",
        "num_instances",
        "optimal_instances",
        "valid_count",
        "best_or_tied_count",
        "mean_makespan",
        "mean_gap",
        "median_gap",
        "mean_runtime",
        "median_runtime",
    ]


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
            summary_rows
        )


# ============================================================
# 8. 主程序
# ============================================================

def main():

    all_results = []


    print("=" * 100)

    print(
        "JSSP Heuristic Benchmark"
    )

    print("=" * 100)

    print(
        f"Rules: "
        f"{', '.join(RULES)}"
    )

    print(
        f"Seeds per size: "
        f"{len(SEEDS)}"
    )

    print(
        f"Gurobi time limit: "
        f"{GUROBI_TIME_LIMIT}s"
    )


    # ========================================================
    # 运行 60 个实例
    # ========================================================

    for (
        num_jobs,
        num_machines,
    ) in SIZES:

        print(
            "\n" + "-" * 100
        )

        print(
            f"Testing "
            f"{num_jobs}x{num_machines}"
        )

        print(
            "-" * 100
        )


        for seed in SEEDS:

            result = (
                run_single_instance(
                    num_jobs=(
                        num_jobs
                    ),
                    num_machines=(
                        num_machines
                    ),
                    seed=seed,
                )
            )


            all_results.append(
                result
            )


            # 当前实例三种 heuristic
            # 的 Makespan

            spt = result[
                "heuristics"
            ]["SPT"]["makespan"]

            lpt = result[
                "heuristics"
            ]["LPT"]["makespan"]

            mwkr = result[
                "heuristics"
            ]["MWKR"]["makespan"]


            print(
                f"seed={seed:<2} | "
                f"Gurobi="
                f"{result['gurobi_status']:<10} | "
                f"SPT={spt:<6.0f} "
                f"LPT={lpt:<6.0f} "
                f"MWKR={mwkr:<6.0f}"
            )


    # ========================================================
    # Summary
    # ========================================================

    summary_rows = (
        build_summary(
            all_results
        )
    )


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
        f"{'Size':<10}"
        f"{'Rule':<8}"
        f"{'MeanGap%':<14}"
        f"{'MedianGap%':<14}"
        f"{'Best/Tied':<14}"
        f"{'Valid':<12}"
        f"{'Runtime(ms)':<14}"
    )

    print(
        "-" * 110
    )


    for row in summary_rows:

        size_text = (
            f"{row['num_jobs']}"
            f"x"
            f"{row['num_machines']}"
        )


        if row["mean_gap"] is None:

            mean_gap_text = "-"
            median_gap_text = "-"

        else:

            mean_gap_text = (
                f"{100 * row['mean_gap']:.2f}"
            )

            median_gap_text = (
                f"{100 * row['median_gap']:.2f}"
            )


        best_text = (
            f"{row['best_or_tied_count']}"
            f"/"
            f"{row['num_instances']}"
        )


        valid_text = (
            f"{row['valid_count']}"
            f"/"
            f"{row['num_instances']}"
        )


        runtime_ms = (
            1000
            * row[
                "median_runtime"
            ]
        )


        print(
            f"{size_text:<10}"
            f"{row['rule']:<8}"
            f"{mean_gap_text:<14}"
            f"{median_gap_text:<14}"
            f"{best_text:<14}"
            f"{valid_text:<12}"
            f"{runtime_ms:<14.4f}"
        )


    # ========================================================
    # 保存文件
    # ========================================================

    instance_file = (
        PROJECT_DIR
        / "heuristic_instance_results.csv"
    )

    summary_file = (
        PROJECT_DIR
        / "heuristic_summary.csv"
    )


    save_instance_results(
        all_results,
        instance_file,
    )

    save_summary(
        summary_rows,
        summary_file,
    )


    print(
        "\n" + "=" * 110
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
        f"总随机实例数量："
        f"{len(all_results)}"
    )


if __name__ == "__main__":

    main()