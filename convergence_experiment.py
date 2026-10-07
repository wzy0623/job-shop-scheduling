# convergence_experiment.py
# ============================================================
# JSSP Difficult Instance Convergence Experiment
# ============================================================

import csv
from pathlib import Path

from random_instance import (
    generate_random_instance,
)

from gurobi_solver import (
    solve_job_shop,
)


PROJECT_DIR = (
    Path(__file__).resolve().parent
)


# ============================================================
# 1. 固定困难实例
# ============================================================

NUM_JOBS = 12
NUM_MACHINES = 12
SEED = 5


# ============================================================
# 2. 不同求解时间
# ============================================================

TIME_LIMITS = [
    1,
    5,
    10,
    30,
]


# ============================================================
# 3. 生成同一个实例
# ============================================================

jobs, machines, big_m = (
    generate_random_instance(
        num_jobs=NUM_JOBS,
        num_machines=NUM_MACHINES,
        processing_time_min=1,
        processing_time_max=10,
        seed=SEED,
    )
)


# ============================================================
# 4. 运行实验
# ============================================================

results = []


print("=" * 100)

print(
    "JSSP Convergence Experiment"
)

print(
    f"Instance: "
    f"{NUM_JOBS}x{NUM_MACHINES}, "
    f"seed={SEED}"
)

print("=" * 100)


print(
    f"{'Limit(s)':<12}"
    f"{'Status':<14}"
    f"{'Incumbent':<14}"
    f"{'Bound':<14}"
    f"{'Gap(%)':<14}"
    f"{'Solutions':<12}"
    f"{'Nodes':<12}"
)


print("-" * 100)


for time_limit in TIME_LIMITS:

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
        time_limit=time_limit,
    )


    incumbent = (
        stats["incumbent"]
    )

    best_bound = (
        stats["best_bound"]
    )

    mip_gap = (
        stats["mip_gap"]
    )


    # ========================================================
    # 显示文本
    # ========================================================

    if incumbent is None:

        incumbent_text = "-"

    else:

        incumbent_text = (
            f"{incumbent:.2f}"
        )


    if best_bound is None:

        bound_text = "-"

    else:

        bound_text = (
            f"{best_bound:.2f}"
        )


    if mip_gap is None:

        gap_text = "-"

    else:

        gap_text = (
            f"{100 * mip_gap:.2f}"
        )


    print(
        f"{time_limit:<12}"
        f"{stats['status']:<14}"
        f"{incumbent_text:<14}"
        f"{bound_text:<14}"
        f"{gap_text:<14}"
        f"{stats['solution_count']:<12}"
        f"{stats['node_count']:<12.0f}"
    )


    # ========================================================
    # 保存
    # ========================================================

    results.append(
        {
            "time_limit": time_limit,
            "status": (
                stats["status"]
            ),
            "runtime": (
                stats["runtime"]
            ),
            "incumbent": incumbent,
            "best_bound": (
                best_bound
            ),
            "mip_gap": mip_gap,
            "solution_count": (
                stats[
                    "solution_count"
                ]
            ),
            "node_count": (
                stats[
                    "node_count"
                ]
            ),
        }
    )


# ============================================================
# 5. 写入 CSV
# ============================================================

output_file = (
    PROJECT_DIR
    / "convergence_results.csv"
)


fieldnames = [
    "time_limit",
    "status",
    "runtime",
    "incumbent",
    "best_bound",
    "mip_gap",
    "solution_count",
    "node_count",
]


with open(
    output_file,
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


print("\n" + "=" * 100)

print(
    f"结果已保存："
    f"{output_file}"
)