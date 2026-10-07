# test_tabu_search.py
# ============================================================
# Compare:
#
# MWKR
# MWKR + Local Search
# MWKR + Tabu Search
# Gurobi
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

from tabu_search import (
    tabu_search,
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
# 2. MWKR
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


# ============================================================
# 3. Local Search
# ============================================================

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


# ============================================================
# 4. Tabu Search
# ============================================================

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
    max_iterations=100,
    tabu_tenure=7,
)


# ============================================================
# 5. Validate Tabu
# ============================================================

print("=" * 75)

print(
    "Tabu Search Validation"
)

print("=" * 75)


tabu_valid = validate_schedule(
    jobs=jobs,
    machines=machines,
    start_times=tabu_start_times,
    cmax_value=tabu_cmax,
)


# ============================================================
# 6. Gurobi
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


# ============================================================
# 7. Summary
# ============================================================

print(
    "\n" + "=" * 90
)

print(
    "Algorithm Comparison"
)

print("=" * 90)


print(
    f"{'Method':<22}"
    f"{'Makespan':<14}"
    f"{'Runtime(ms)':<16}"
    f"{'Gap(%)':<14}"
)

print("-" * 90)


# ============================================================
# Gap helper
# ============================================================

def gap_text(cmax):

    if (
        optimal_start_times is None
        or
        gurobi_stats["status"]
        != "OPTIMAL"
    ):

        return "-"

    gap = (
        (
            cmax
            - optimal_cmax
        )
        / optimal_cmax
    )

    return (
        f"{100 * gap:.2f}"
    )


print(
    f"{'MWKR':<22}"
    f"{mwkr_cmax:<14.0f}"
    f"{1000 * mwkr_stats['runtime']:<16.4f}"
    f"{gap_text(mwkr_cmax):<14}"
)


print(
    f"{'MWKR + Local Search':<22}"
    f"{local_cmax:<14.0f}"
    f"{1000 * local_stats['runtime']:<16.4f}"
    f"{gap_text(local_cmax):<14}"
)


print(
    f"{'MWKR + Tabu Search':<22}"
    f"{tabu_cmax:<14.0f}"
    f"{1000 * tabu_stats['runtime']:<16.4f}"
    f"{gap_text(tabu_cmax):<14}"
)


if (
    optimal_start_times is not None
    and
    gurobi_stats["status"]
    == "OPTIMAL"
):

    print(
        f"{'Gurobi Optimal':<22}"
        f"{optimal_cmax:<14.0f}"
        f"{1000 * gurobi_stats['runtime']:<16.4f}"
        f"{'0.00':<14}"
    )


# ============================================================
# 8. Tabu Statistics
# ============================================================

print(
    "\n" + "=" * 90
)

print(
    "Tabu Search Statistics"
)

print("=" * 90)


print(
    f"Iterations: "
    f"{tabu_stats['iterations']}"
)

print(
    f"Evaluated moves: "
    f"{tabu_stats['evaluated_moves']}"
)

print(
    f"Feasible moves: "
    f"{tabu_stats['feasible_moves']}"
)

print(
    f"Tabu skipped: "
    f"{tabu_stats['tabu_skipped']}"
)

print(
    f"Aspiration uses: "
    f"{tabu_stats['aspiration_uses']}"
)

print(
    f"Accepted worsening moves: "
    f"{tabu_stats['accepted_worsening_moves']}"
)

print(
    f"Accepted equal moves: "
    f"{tabu_stats['accepted_equal_moves']}"
)

print(
    f"Best improvements: "
    f"{tabu_stats['best_improvements']}"
)


# ============================================================
# 9. Plot
# ============================================================

if tabu_valid:

    plot_gantt(
        jobs=jobs,
        machines=machines,
        start_times=tabu_start_times,
        cmax_value=tabu_cmax,
        filename=(
            "tabu_search_10x10_gantt.png"
        ),
        show=True,
    )