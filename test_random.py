# test_random.py
# ============================================================
# Test Random Job Shop Scheduling Instance
# ============================================================

from random_instance import (
    generate_random_instance,
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
# 1. 实验参数
# ============================================================

NUM_JOBS = 5
NUM_MACHINES = 5

SEED = 42


# ============================================================
# 2. 生成随机实例
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
# 3. 打印实例
# ============================================================

print("=" * 60)

print(
    f"Random JSSP Instance: "
    f"{NUM_JOBS} Jobs x "
    f"{NUM_MACHINES} Machines"
)

print("=" * 60)


for job_id, operations in jobs.items():

    print(
        f"\nJob {job_id}:"
    )

    for operation_index, (
        machine_id,
        processing_time,
    ) in enumerate(
        operations,
        start=1,
    ):

        print(
            f"  Operation {operation_index}: "
            f"M{machine_id}, "
            f"processing time = "
            f"{processing_time}"
        )


print(
    f"\nBig-M = {big_m}"
)


# ============================================================
# 4. Gurobi 求解
# ============================================================

start_times, cmax_value = (
    solve_job_shop(
        jobs=jobs,
        machines=machines,
        big_m=big_m,
        verbose=False,
    )
)


# ============================================================
# 5. 检查是否求解成功
# ============================================================

if start_times is None:

    print(
        "\n没有找到最优解。"
    )

    raise SystemExit


# ============================================================
# 6. 输出结果
# ============================================================

print(
    f"\n最优 Makespan = "
    f"{cmax_value:.0f}"
)


# ============================================================
# 7. Validator
# ============================================================

validation_ok = (
    validate_schedule(
        jobs=jobs,
        machines=machines,
        start_times=start_times,
        cmax_value=cmax_value,
    )
)


# ============================================================
# 8. Gantt Chart
# ============================================================

if validation_ok:

    plot_gantt(
        jobs=jobs,
        machines=machines,
        start_times=start_times,
        cmax_value=cmax_value,
        filename="random_5x5_gantt.png",
        show=True,
    )