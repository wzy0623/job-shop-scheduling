# test_local_search.py
# ============================================================
# MWKR + Adjacent-Swap Local Search
# ============================================================

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
    validate_schedule,
)

from gantt_chart import (
    plot_gantt,
)


# ============================================================
# 1. Instance
# ============================================================

NUM_JOBS = 10
NUM_MACHINES = 10
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
# 2. MWKR Initial Solution
# ============================================================

(
    mwkr_start_times,
    mwkr_cmax,
    mwkr_stats,
) = solve_with_dispatching_rule(
    jobs=jobs,
    machines=machines,
    rule="MWKR",
)


print("=" * 70)

print(
    "MWKR Initial Solution"
)

print("=" * 70)

print(
    f"Makespan = "
    f"{mwkr_cmax:.0f}"
)

print(
    f"Runtime = "
    f"{1000 * mwkr_stats['runtime']:.4f} ms"
)


mwkr_valid = validate_schedule(
    jobs=jobs,
    machines=machines,
    start_times=mwkr_start_times,
    cmax_value=mwkr_cmax,
)


# ============================================================
# 3. Local Search
# ============================================================

(
    improved_start_times,
    improved_cmax,
    local_stats,
) = improve_with_adjacent_swaps(
    jobs=jobs,
    machines=machines,
    initial_start_times=(
        mwkr_start_times
    ),
    max_iterations=100,
)


print(
    "\n" + "=" * 70
)

print(
    "MWKR + Local Search"
)

print("=" * 70)

print(
    f"Initial MWKR Makespan = "
    f"{mwkr_cmax:.0f}"
)

print(
    f"Final Makespan = "
    f"{improved_cmax:.0f}"
)

print(
    f"Local Search Iterations = "
    f"{local_stats['iterations']}"
)

print(
    f"Evaluated Moves = "
    f"{local_stats['evaluated_moves']}"
)

print(
    f"Feasible Moves = "
    f"{local_stats['feasible_moves']}"
)

print(
    f"Local Search Runtime = "
    f"{1000 * local_stats['runtime']:.4f} ms"
)


# ============================================================
# 4. Improvement
# ============================================================

improvement = (
    (
        mwkr_cmax
        - improved_cmax
    )
    / mwkr_cmax
)


print(
    f"Improvement over MWKR = "
    f"{100 * improvement:.2f}%"
)


# ============================================================
# 5. Validator
# ============================================================

local_valid = validate_schedule(
    jobs=jobs,
    machines=machines,
    start_times=(
        improved_start_times
    ),
    cmax_value=improved_cmax,
)


# ============================================================
# 6. Gurobi
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "Gurobi Comparison"
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

    mwkr_gap = (
        (
            mwkr_cmax
            - optimal_cmax
        )
        / optimal_cmax
    )

    local_gap = (
        (
            improved_cmax
            - optimal_cmax
        )
        / optimal_cmax
    )


    print(
        f"Optimal Makespan = "
        f"{optimal_cmax:.0f}"
    )

    print(
        f"MWKR Gap = "
        f"{100 * mwkr_gap:.2f}%"
    )

    print(
        f"Local Search Gap = "
        f"{100 * local_gap:.2f}%"
    )

else:

    print(
        "Gurobi 未在 30 秒内证明最优。"
    )

    if (
        gurobi_stats[
            "incumbent"
        ]
        is not None
    ):

        print(
            f"Gurobi Incumbent = "
            f"{gurobi_stats['incumbent']:.2f}"
        )

        print(
            f"Gurobi Best Bound = "
            f"{gurobi_stats['best_bound']:.2f}"
        )

        print(
            f"Gurobi MIP Gap = "
            f"{100 * gurobi_stats['mip_gap']:.2f}%"
        )


# ============================================================
# 7. Plot Improved Schedule
# ============================================================

if local_valid:

    plot_gantt(
        jobs=jobs,
        machines=machines,
        start_times=(
            improved_start_times
        ),
        cmax_value=(
            improved_cmax
        ),
        filename=(
            "local_search_10x10_gantt.png"
        ),
        show=True,
    )