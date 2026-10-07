# compare_heuristics.py
# ============================================================
# Compare SPT / LPT / MWKR with Gurobi Optimal Solution
# ============================================================

from random_instance import (
    generate_random_instance,
)

from heuristic_solver import (
    solve_with_dispatching_rule,
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
# 1. 固定测试实例
# ============================================================

NUM_JOBS = 5
NUM_MACHINES = 5
SEED = 42


RULES = [
    "SPT",
    "LPT",
    "MWKR",
]


# ============================================================
# 2. 生成同一个随机实例
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
# 3. Gurobi 求最优解
# ============================================================

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


gurobi_optimal = (
    optimal_start_times is not None
    and gurobi_stats["status"]
    == "OPTIMAL"
)


if gurobi_optimal:

    print(
        f"\nGurobi Optimal Makespan = "
        f"{optimal_cmax:.0f}"
    )

else:

    print(
        "\nGurobi 未在时间限制内证明最优。"
    )


# ============================================================
# 4. 运行三种 Heuristic
# ============================================================

results = []


for rule in RULES:

    print(
        "\n" + "=" * 70
    )

    print(
        f"Testing {rule}"
    )

    print(
        "=" * 70
    )


    (
        start_times,
        cmax_value,
        stats,
    ) = solve_with_dispatching_rule(
        jobs=jobs,
        machines=machines,
        rule=rule,
    )


    # ========================================================
    # Validator
    # ========================================================

    valid = validate_schedule(
        jobs=jobs,
        machines=machines,
        start_times=start_times,
        cmax_value=cmax_value,
    )


    # ========================================================
    # Heuristic Gap
    # ========================================================

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


    results.append(
        {
            "rule": rule,
            "start_times": (
                start_times
            ),
            "makespan": (
                cmax_value
            ),
            "runtime": (
                stats["runtime"]
            ),
            "valid": valid,
            "gap": gap,
        }
    )


# ============================================================
# 5. Summary
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "Heuristic Comparison"
)

print(
    "=" * 80
)


print(
    f"{'Rule':<10}"
    f"{'Makespan':<14}"
    f"{'Runtime(ms)':<16}"
    f"{'Gap(%)':<14}"
    f"{'Valid':<10}"
)

print(
    "-" * 80
)


for result in results:

    if result["gap"] is None:

        gap_text = "-"

    else:

        gap_text = (
            f"{100 * result['gap']:.2f}"
        )


    runtime_ms = (
        1000
        * result["runtime"]
    )


    print(
        f"{result['rule']:<10}"
        f"{result['makespan']:<14.0f}"
        f"{runtime_ms:<16.4f}"
        f"{gap_text:<14}"
        f"{str(result['valid']):<10}"
    )


# ============================================================
# 6. 找出当前最好的 Heuristic
# ============================================================

valid_results = [
    result
    for result in results
    if result["valid"]
]


best_result = min(
    valid_results,
    key=lambda x: x["makespan"],
)


print(
    "\nBest heuristic on this instance:"
)

print(
    f"{best_result['rule']} "
    f"(Makespan = "
    f"{best_result['makespan']:.0f})"
)


# ============================================================
# 7. 绘制最佳 Heuristic Gantt Chart
# ============================================================

plot_gantt(
    jobs=jobs,
    machines=machines,
    start_times=(
        best_result[
            "start_times"
        ]
    ),
    cmax_value=(
        best_result[
            "makespan"
        ]
    ),
    filename=(
        "best_heuristic_gantt.png"
    ),
    show=True,
)