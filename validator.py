# validator.py
# ============================================================
# Job Shop Scheduling 解的自动验证器
# ============================================================

import math


TOL = 1e-6


# ============================================================
# 1. 检查 Job precedence
# ============================================================
#
# 对同一个 Job：
#
# S[i,j+1] >= S[i,j] + p[i,j]
#
# 即：
# 后一道工序不能早于前一道工序完成。
# ============================================================

def check_job_precedence(jobs, start_times):
    for job_id, operations in jobs.items():

        for operation_index in range(1, len(operations)):

            current_start = start_times[
                job_id,
                operation_index
            ]

            current_processing_time = operations[
                operation_index - 1
            ][1]

            next_start = start_times[
                job_id,
                operation_index + 1
            ]

            current_end = (
                current_start
                + current_processing_time
            )

            # 如果下一道工序开始时间
            # 早于当前工序结束时间
            if next_start < current_end - TOL:

                print(
                    f"  FAIL: Job {job_id}, "
                    f"Operation {operation_index} "
                    f"ends at {current_end:.2f}, "
                    f"but Operation {operation_index + 1} "
                    f"starts at {next_start:.2f}"
                )

                return False

    return True


# ============================================================
# 2. 检查 Machine non-overlap
# ============================================================
#
# 同一台机器上：
#
# 任意两个工序不能发生时间重叠。
#
# 方法：
#
# 1. 找出该机器上的所有工序
# 2. 按开始时间排序
# 3. 检查相邻两个工序是否重叠
# ============================================================

def check_machine_non_overlap(
    jobs,
    machines,
    start_times,
):

    for machine_id in machines:

        schedule = []

        # --------------------------------------------
        # 找出当前机器上的所有工序
        # --------------------------------------------

        for job_id, operations in jobs.items():

            for operation_index, (
                operation_machine,
                processing_time,
            ) in enumerate(
                operations,
                start=1,
            ):

                if operation_machine != machine_id:
                    continue

                start_time = start_times[
                    job_id,
                    operation_index
                ]

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
        schedule.sort(key=lambda x: x[0])

        # --------------------------------------------
        # 检查相邻工序
        # --------------------------------------------

        for i in range(len(schedule) - 1):

            (
                start_a,
                end_a,
                job_a,
                op_a,
            ) = schedule[i]

            (
                start_b,
                end_b,
                job_b,
                op_b,
            ) = schedule[i + 1]

            # 如果 B 在 A 完成之前已经开始
            # 就发生了机器冲突
            if start_b < end_a - TOL:

                print(
                    f"  FAIL: Machine {machine_id} conflict: "
                    f"J{job_a}-O{op_a} "
                    f"[{start_a:.2f}, {end_a:.2f}) "
                    f"overlaps with "
                    f"J{job_b}-O{op_b} "
                    f"[{start_b:.2f}, {end_b:.2f})"
                )

                return False

    return True


# ============================================================
# 3. 检查 Makespan
# ============================================================
#
# 实际 Makespan：
#
# max_i {
#     最后一道工序开始时间
#     +
#     最后一道工序加工时间
# }
#
# 应该与模型返回的 Cmax 一致。
# ============================================================

def check_makespan(
    jobs,
    start_times,
    cmax_value,
):

    actual_makespan = 0.0

    for job_id, operations in jobs.items():

        last_operation_index = len(operations)

        last_processing_time = operations[-1][1]

        last_start = start_times[
            job_id,
            last_operation_index
        ]

        completion_time = (
            last_start
            + last_processing_time
        )

        actual_makespan = max(
            actual_makespan,
            completion_time,
        )

    if not math.isclose(
        actual_makespan,
        cmax_value,
        rel_tol=TOL,
        abs_tol=TOL,
    ):

        print(
            f"  FAIL: model Cmax = {cmax_value:.2f}, "
            f"actual Cmax = {actual_makespan:.2f}"
        )

        return False

    return True


# ============================================================
# 4. 总体验证
# ============================================================

def validate_schedule(
    jobs,
    machines,
    start_times,
    cmax_value,
):

    print("\n" + "=" * 60)
    print("Validation")
    print("=" * 60)

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

    print(
        f"Job precedence:       "
        f"{'PASS' if precedence_ok else 'FAIL'}"
    )

    print(
        f"Machine non-overlap:  "
        f"{'PASS' if machine_ok else 'FAIL'}"
    )

    print(
        f"Makespan:             "
        f"{'PASS' if makespan_ok else 'FAIL'}"
    )

    overall_ok = (
        precedence_ok
        and machine_ok
        and makespan_ok
    )

    print()

    print(
        f"Overall validation:   "
        f"{'PASS' if overall_ok else 'FAIL'}"
    )

    return overall_ok