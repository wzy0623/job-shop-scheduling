# main.py
# ============================================================
# Job Shop Scheduling Project
# ============================================================

from instance import (
    JOBS,
    MACHINES,
    BIG_M,
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
# 1. 求解 Job Shop Scheduling
# ============================================================

start_times, cmax_value = (
    solve_job_shop(
        jobs=JOBS,
        machines=MACHINES,
        big_m=BIG_M,
        verbose=False,
    )
)


# ============================================================
# 2. 检查是否成功求得最优解
# ============================================================

if start_times is None:

    print(
        "没有找到最优解。"
    )

    raise SystemExit


# ============================================================
# 3. 输出最优 Makespan
# ============================================================

print("=" * 60)

print(
    "Job Shop Scheduling"
)

print("=" * 60)

print(
    f"\n最优 Makespan = "
    f"{cmax_value:.0f}"
)


# ============================================================
# 4. 按 Job 输出调度
# ============================================================

print(
    "\n每个 Job 的调度："
)


for job_id, operations in JOBS.items():

    print(
        f"\nJob {job_id}"
    )

    for operation_index, (
        machine_id,
        processing_time,
    ) in enumerate(
        operations,
        start=1,
    ):

        start_time = (
            start_times[
                job_id,
                operation_index,
            ]
        )

        end_time = (
            start_time
            + processing_time
        )

        print(
            f"  Operation "
            f"{operation_index}: "
            f"M{machine_id}, "
            f"start = "
            f"{start_time:.0f}, "
            f"end = "
            f"{end_time:.0f}"
        )


# ============================================================
# 5. 按机器输出调度
# ============================================================

print(
    "\n" + "=" * 60
)

print(
    "按机器查看："
)


for machine_id in MACHINES:

    schedule = []

    for job_id, operations in JOBS.items():

        for operation_index, (
            operation_machine,
            processing_time,
        ) in enumerate(
            operations,
            start=1,
        ):

            if (
                operation_machine
                != machine_id
            ):

                continue


            start_time = (
                start_times[
                    job_id,
                    operation_index,
                ]
            )

            end_time = (
                start_time
                + processing_time
            )


            schedule.append(
                (
                    start_time,
                    end_time,
                    job_id,
                    operation_index,
                )
            )


    # 按开始时间排序

    schedule.sort(
        key=lambda x: x[0]
    )


    print(
        f"\nMachine {machine_id}"
    )


    for (
        start_time,
        end_time,
        job_id,
        operation_index,
    ) in schedule:

        print(
            f"  J{job_id}-"
            f"O{operation_index}: "
            f"{start_time:.0f} "
            f"-> "
            f"{end_time:.0f}"
        )


# ============================================================
# 6. 自动验证
# ============================================================

validation_ok = (
    validate_schedule(
        jobs=JOBS,
        machines=MACHINES,
        start_times=start_times,
        cmax_value=cmax_value,
    )
)


# ============================================================
# 7. 绘制 Gantt Chart
# ============================================================

if validation_ok:

    plot_gantt(
        jobs=JOBS,
        machines=MACHINES,
        start_times=start_times,
        cmax_value=cmax_value,
        filename="gantt_chart.png",
        show=True,
    )