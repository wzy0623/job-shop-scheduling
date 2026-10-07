# heuristic_solver.py
# ============================================================
# Job Shop Scheduling
# Dispatching Rule Heuristics
#
# Supported rules:
#   SPT  - Shortest Processing Time
#   LPT  - Longest Processing Time
#   MWKR - Most Work Remaining
# ============================================================

import time


VALID_RULES = {
    "SPT",
    "LPT",
    "MWKR",
}


def solve_with_dispatching_rule(
    jobs,
    machines,
    rule="SPT",
):
    """
    使用 Dispatching Rule 构造一个可行 JSSP 调度。

    基本框架：
    1. 每个 Job 只考虑下一道尚未调度的工序；
    2. 计算这些工序的 earliest start；
    3. 优先选择 earliest start 最小的候选；
    4. 若 earliest start 相同，再使用指定规则排序。

    Parameters
    ----------
    jobs:
        Job 数据。

    machines:
        Machine 编号列表。

    rule:
        "SPT"
        "LPT"
        "MWKR"

    Returns
    -------
    start_times:
        {(job_id, operation_index): start_time}

    cmax_value:
        Makespan

    stats:
        运行时间、规则等统计信息。
    """

    rule = rule.upper()

    if rule not in VALID_RULES:

        raise ValueError(
            f"Unsupported rule: {rule}. "
            f"Choose from {sorted(VALID_RULES)}."
        )


    start_clock = time.perf_counter()


    # ========================================================
    # 1. 每个 Job 下一道尚未调度的工序
    # ========================================================
    #
    # 使用 0-based index。
    # ========================================================

    next_operation = {
        job_id: 0
        for job_id in jobs
    }


    # ========================================================
    # 2. Job Ready Time
    # ========================================================

    job_ready_time = {
        job_id: 0.0
        for job_id in jobs
    }


    # ========================================================
    # 3. Machine Ready Time
    # ========================================================

    machine_ready_time = {
        machine_id: 0.0
        for machine_id in machines
    }


    # ========================================================
    # 4. 保存调度结果
    # ========================================================

    start_times = {}


    # ========================================================
    # 5. 总工序数量
    # ========================================================

    total_operations = sum(
        len(operations)
        for operations in jobs.values()
    )

    scheduled_operations = 0


    # ========================================================
    # 6. 主循环
    # ========================================================

    while scheduled_operations < total_operations:

        candidates = []


        # ----------------------------------------------------
        # 每个 Job 提供下一道尚未调度的工序
        # ----------------------------------------------------

        for job_id, operations in jobs.items():

            operation_index = (
                next_operation[job_id]
            )


            # Job 已经全部完成
            if operation_index >= len(
                operations
            ):
                continue


            (
                machine_id,
                processing_time,
            ) = operations[
                operation_index
            ]


            # ------------------------------------------------
            # Earliest Start
            # ------------------------------------------------
            #
            # 必须同时满足：
            #
            # 1. Job 前一道工序已经完成
            # 2. Machine 已经空闲
            # ------------------------------------------------

            earliest_start = max(
                job_ready_time[job_id],
                machine_ready_time[
                    machine_id
                ],
            )


            # ------------------------------------------------
            # Remaining Work
            # ------------------------------------------------
            #
            # 当前工序 + 后续所有工序的加工时间
            # ------------------------------------------------

            remaining_work = sum(
                p
                for _, p
                in operations[
                    operation_index:
                ]
            )


            candidates.append(
                {
                    "earliest_start": (
                        earliest_start
                    ),
                    "processing_time": (
                        processing_time
                    ),
                    "remaining_work": (
                        remaining_work
                    ),
                    "job_id": job_id,
                    "operation_index": (
                        operation_index
                    ),
                    "machine_id": (
                        machine_id
                    ),
                }
            )


        # ====================================================
        # 7. Dispatching Priority
        # ====================================================

        def priority(candidate):

            earliest_start = (
                candidate[
                    "earliest_start"
                ]
            )

            processing_time = (
                candidate[
                    "processing_time"
                ]
            )

            remaining_work = (
                candidate[
                    "remaining_work"
                ]
            )

            job_id = (
                candidate["job_id"]
            )


            # -----------------------------------------------
            # SPT
            #
            # processing time 越小越优先
            # -----------------------------------------------

            if rule == "SPT":

                return (
                    earliest_start,
                    processing_time,
                    job_id,
                )


            # -----------------------------------------------
            # LPT
            #
            # processing time 越大越优先
            #
            # Python min()，
            # 所以使用负号。
            # -----------------------------------------------

            if rule == "LPT":

                return (
                    earliest_start,
                    -processing_time,
                    job_id,
                )


            # -----------------------------------------------
            # MWKR
            #
            # remaining work 越大越优先
            # -----------------------------------------------

            return (
                earliest_start,
                -remaining_work,
                job_id,
            )


        selected = min(
            candidates,
            key=priority,
        )


        # ====================================================
        # 8. 读取选中的工序
        # ====================================================

        job_id = (
            selected["job_id"]
        )

        operation_index = (
            selected[
                "operation_index"
            ]
        )

        machine_id = (
            selected["machine_id"]
        )

        processing_time = (
            selected[
                "processing_time"
            ]
        )

        start_time = (
            selected[
                "earliest_start"
            ]
        )

        end_time = (
            start_time
            + processing_time
        )


        # ====================================================
        # 9. 保存调度
        # ========================================================
        #
        # Validator 使用 1-based operation index。
        # ========================================================

        start_times[
            job_id,
            operation_index + 1,
        ] = start_time


        # ====================================================
        # 10. 更新状态
        # ========================================================

        job_ready_time[
            job_id
        ] = end_time

        machine_ready_time[
            machine_id
        ] = end_time

        next_operation[
            job_id
        ] += 1

        scheduled_operations += 1


    # ========================================================
    # 11. Makespan
    # ========================================================

    cmax_value = max(
        job_ready_time.values()
    )


    # ========================================================
    # 12. Runtime
    # ========================================================

    runtime = (
        time.perf_counter()
        - start_clock
    )


    stats = {
        "rule": rule,
        "runtime": runtime,
        "scheduled_operations": (
            scheduled_operations
        ),
    }


    return (
        start_times,
        cmax_value,
        stats,
    )


# ============================================================
# Backward-compatible wrappers
# ============================================================

def solve_with_spt(
    jobs,
    machines,
):
    return solve_with_dispatching_rule(
        jobs=jobs,
        machines=machines,
        rule="SPT",
    )


def solve_with_lpt(
    jobs,
    machines,
):
    return solve_with_dispatching_rule(
        jobs=jobs,
        machines=machines,
        rule="LPT",
    )


def solve_with_mwkr(
    jobs,
    machines,
):
    return solve_with_dispatching_rule(
        jobs=jobs,
        machines=machines,
        rule="MWKR",
    )