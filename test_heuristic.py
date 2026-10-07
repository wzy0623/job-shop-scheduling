# test_heuristic.py
# ============================================================
# Compare JSSP Heuristic with Gurobi
# ============================================================

from random_instance import (
    generate_random_instance,
)

from heuristic_solver import (
    solve_with_spt,
)

from gurobi_solver import (
    solve_job_shop,
)

from validator import (
    validate_schedule,
)

from gantt_chart import (
    plot_gantt,
)


# ============================================================
# 1. 测试实例
# ============================================================

NUM_JOBS = 5
NUM_MACHINES = 5
SEED = 42


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
# 2. SPT Heuristic
# ============================================================

(
    heuristic_start_times,
    heuristic_cmax,
    heuristic_stats,
) = solve_with_spt(
    jobs=jobs,
    machines=machines,
)


# ============================================================
# 3. 验证 Heuristic 解
# ============================================================

print("=" * 70)

print(
    "SPT Heuristic"
)

print("=" * 70)

print(
    f"Makespan = "
    f"{heuristic_cmax:.0f}"
)

print(
    f"Runtime = "
    f"{heuristic_stats['runtime']:.6f} s"
)


heuristic_valid = (
    validate_schedule(
        jobs=jobs,
        machines=machines,
        start_times=(
            heuristic_start_times
        ),
        cmax_value=heuristic_cmax,
    )
)


# ============================================================
# 4. Gurobi Optimal Solution
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "Gurobi"
)

print("=" * 70)


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
    time_limit=30,
)


if (
    optimal_start_times is not None
    and gurobi_stats["status"]
    == "OPTIMAL"
):

    print(
        f"Optimal Makespan = "
        f"{optimal_cmax:.0f}"
    )

    print(
        f"Gurobi Runtime = "
        f"{gurobi_stats['runtime']:.6f} s"
    )


    # ========================================================
    # 5. Heuristic Gap
    # ========================================================

    heuristic_gap = (
        (
            heuristic_cmax
            - optimal_cmax
        )
        / optimal_cmax
    )


    print(
        f"Heuristic Gap = "
        f"{100 * heuristic_gap:.2f}%"
    )


else:

    print(
        "Gurobi 未在时间限制内证明最优。"
    )

    heuristic_gap = None


# ============================================================
# 6. 绘制 Heuristic Gantt Chart
# ============================================================

if heuristic_valid:

    plot_gantt(
        jobs=jobs,
        machines=machines,
        start_times=(
            heuristic_start_times
        ),
        cmax_value=heuristic_cmax,
        filename=(
            "heuristic_5x5_gantt.png"
        ),
        show=True,
    )