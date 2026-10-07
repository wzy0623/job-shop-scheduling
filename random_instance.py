# random_instance.py
# ============================================================
# Random Job Shop Scheduling Instance Generator
# ============================================================

import random


def generate_random_instance(
    num_jobs,
    num_machines,
    processing_time_min=1,
    processing_time_max=10,
    seed=None,
):
    """
    随机生成一个 Job Shop Scheduling 实例。

    Parameters
    ----------
    num_jobs:
        Job 数量。

    num_machines:
        Machine 数量。

    processing_time_min:
        最小加工时间。

    processing_time_max:
        最大加工时间。

    seed:
        随机种子，用于保证实验可重复。

    Returns
    -------
    jobs:
        {
            job_id: [
                (machine_id, processing_time),
                ...
            ]
        }

    machines:
        机器编号列表。

    big_m:
        Big-M 常数。
    """

    # ========================================================
    # 1. 创建独立随机数生成器
    # ========================================================

    rng = random.Random(seed)


    # ========================================================
    # 2. Machine 编号
    # ========================================================

    machines = list(
        range(1, num_machines + 1)
    )


    # ========================================================
    # 3. 生成 Jobs
    # ========================================================

    jobs = {}

    for job_id in range(
        1,
        num_jobs + 1,
    ):

        # ----------------------------------------------------
        # 每个 Job 随机生成一个 Machine permutation
        #
        # 例如：
        #
        # [1, 2, 3, 4, 5]
        #
        # 可能变成：
        #
        # [3, 1, 5, 2, 4]
        # ----------------------------------------------------

        machine_order = rng.sample(
            machines,
            len(machines),
        )


        operations = []

        for machine_id in machine_order:

            processing_time = rng.randint(
                processing_time_min,
                processing_time_max,
            )

            operations.append(
                (
                    machine_id,
                    processing_time,
                )
            )


        jobs[job_id] = operations


    # ========================================================
    # 4. Big-M
    # ========================================================
    #
    # 所有加工时间之和是一个安全的 Makespan 上界。
    #
    # 最坏情况下：
    #
    # 所有工序完全串行执行。
    # ========================================================

    big_m = sum(
        processing_time
        for operations in jobs.values()
        for _, processing_time in operations
    )


    return (
        jobs,
        machines,
        big_m,
    )