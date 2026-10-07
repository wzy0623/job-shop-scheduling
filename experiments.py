# experiments.py
# ============================================================
# Job Shop Scheduling - Multi-instance Size Benchmark
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


PROJECT_DIR = Path(__file__).resolve().parent


# ============================================================
# 1. 实验设置
# ============================================================

SIZES = [
    (3, 3),
    (5, 5),
    (7, 7),
    (10, 10),
    (12, 12),
]

# 每个规模测试 10 个随机实例
SEEDS = list(range(10))

# 单个实例最长求解 30 秒
TIME_LIMIT = 30


# ============================================================
# 2. 单个实例实验
# ============================================================

def run_single_experiment(
    num_jobs,
    num_machines,
    seed,
):
    jobs, machines, big_m = (
        generate_random_instance(
            num_jobs=num_jobs,
            num_machines=num_machines,
            processing_time_min=1,
            processing_time_max=10,
            seed=seed,
        )
    )


    (
        start_times,
        cmax_value,
        stats,
    ) = solve_job_shop(
        jobs=jobs,
        machines=machines,
        big_m=big_m,
        verbose=False,
        return_stats=True,
        time_limit=TIME_LIMIT,
    )


    return {
        "num_jobs": num_jobs,
        "num_machines": num_machines,
        "seed": seed,
        "status": stats["status"],
        "makespan": cmax_value,
        "runtime": stats["runtime"],
        "num_variables": stats[
            "num_variables"
        ],
        "num_constraints": stats[
            "num_constraints"
        ],
    }


# ============================================================
# 3. 对一个规模运行多个 seed
# ============================================================

def run_size_experiment(
    num_jobs,
    num_machines,
):
    instance_results = []


    for seed in SEEDS:

        result = run_single_experiment(
            num_jobs=num_jobs,
            num_machines=num_machines,
            seed=seed,
        )

        instance_results.append(result)


        print(
            f"{num_jobs}x{num_machines}, "
            f"seed={seed:<2} | "
            f"{result['status']:<10} | "
            f"runtime="
            f"{result['runtime']:.4f}s"
        )


    # ========================================================
    # Runtime statistics
    # ========================================================

    runtimes = [
        result["runtime"]
        for result in instance_results
    ]


    optimal_results = [
        result
        for result in instance_results
        if result["status"] == "OPTIMAL"
    ]


    optimal_count = len(
        optimal_results
    )

    time_limit_count = sum(
        result["status"] == "TIME_LIMIT"
        for result in instance_results
    )


    # ========================================================
    # Makespan 平均值
    #
    # 只统计已经证明最优的实例
    # ========================================================

    optimal_makespans = [
        result["makespan"]
        for result in optimal_results
        if result["makespan"] is not None
    ]

    if optimal_makespans:

        mean_makespan = statistics.mean(
            optimal_makespans
        )

    else:

        mean_makespan = None


    # ========================================================
    # 汇总结果
    # ========================================================

    summary = {
        "num_jobs": num_jobs,
        "num_machines": num_machines,
        "num_instances": len(
            instance_results
        ),
        "optimal_count": optimal_count,
        "time_limit_count": (
            time_limit_count
        ),
        "mean_runtime": statistics.mean(
            runtimes
        ),
        "median_runtime": statistics.median(
            runtimes
        ),
        "std_runtime": (
            statistics.stdev(runtimes)
            if len(runtimes) > 1
            else 0.0
        ),
        "mean_makespan": mean_makespan,
        "num_variables": (
            instance_results[0][
                "num_variables"
            ]
        ),
        "num_constraints": (
            instance_results[0][
                "num_constraints"
            ]
        ),
    }


    return (
        instance_results,
        summary,
    )


# ============================================================
# 4. 保存逐实例结果
# ============================================================

def save_instance_results(
    results,
    filename,
):
    fieldnames = [
        "num_jobs",
        "num_machines",
        "seed",
        "status",
        "makespan",
        "runtime",
        "num_variables",
        "num_constraints",
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

        writer.writerows(results)


# ============================================================
# 5. 保存汇总结果
# ============================================================

def save_summary_results(
    results,
    filename,
):
    fieldnames = [
        "num_jobs",
        "num_machines",
        "num_instances",
        "optimal_count",
        "time_limit_count",
        "mean_runtime",
        "median_runtime",
        "std_runtime",
        "mean_makespan",
        "num_variables",
        "num_constraints",
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

        writer.writerows(results)


# ============================================================
# 6. 主程序
# ============================================================

def main():

    all_instance_results = []

    all_summary_results = []


    print("=" * 80)

    print(
        "Job Shop Scheduling - "
        "Multi-instance Benchmark"
    )

    print("=" * 80)

    print(
        f"Seeds per size: "
        f"{len(SEEDS)}"
    )

    print(
        f"Time limit: "
        f"{TIME_LIMIT} seconds"
    )


    # ========================================================
    # 运行实验
    # ========================================================

    for (
        num_jobs,
        num_machines,
    ) in SIZES:

        print(
            "\n" + "-" * 80
        )

        print(
            f"Testing "
            f"{num_jobs}x{num_machines}"
        )

        print(
            "-" * 80
        )


        (
            instance_results,
            summary,
        ) = run_size_experiment(
            num_jobs=num_jobs,
            num_machines=num_machines,
        )


        all_instance_results.extend(
            instance_results
        )

        all_summary_results.append(
            summary
        )


    # ========================================================
    # 7. 输出 Summary
    # ========================================================

    print(
        "\n" + "=" * 100
    )

    print(
        "Summary"
    )

    print(
        "=" * 100
    )


    print(
        f"{'Size':<10}"
        f"{'Optimal':<12}"
        f"{'Mean(s)':<14}"
        f"{'Median(s)':<14}"
        f"{'Std(s)':<14}"
        f"{'Variables':<12}"
        f"{'Constraints':<12}"
    )

    print(
        "-" * 100
    )


    for result in all_summary_results:

        size_text = (
            f"{result['num_jobs']}"
            f"x"
            f"{result['num_machines']}"
        )


        optimal_text = (
            f"{result['optimal_count']}"
            f"/"
            f"{result['num_instances']}"
        )


        print(
            f"{size_text:<10}"
            f"{optimal_text:<12}"
            f"{result['mean_runtime']:<14.4f}"
            f"{result['median_runtime']:<14.4f}"
            f"{result['std_runtime']:<14.4f}"
            f"{result['num_variables']:<12}"
            f"{result['num_constraints']:<12}"
        )


    # ========================================================
    # 8. 保存 CSV
    # ========================================================

    instance_file = (
        PROJECT_DIR
        / "instance_results.csv"
    )

    summary_file = (
        PROJECT_DIR
        / "experiment_summary.csv"
    )


    save_instance_results(
        all_instance_results,
        instance_file,
    )

    save_summary_results(
        all_summary_results,
        summary_file,
    )


    print(
        "\n" + "=" * 100
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
        f"{len(all_instance_results)}"
    )


if __name__ == "__main__":

    main()