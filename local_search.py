# local_search.py
# ============================================================
# Job Shop Scheduling
# Adjacent-Swap Local Search
# ============================================================

import heapq
import time


# ============================================================
# 1. 从已有 Schedule 提取每台机器的加工顺序
# ============================================================

def build_machine_sequences(
    jobs,
    machines,
    start_times,
):
    """
    根据一个可行调度的开始时间，
    提取每台机器上的工序顺序。

    Returns
    -------
    machine_sequences:

        {
            machine_id: [
                (job_id, operation_index),
                ...
            ]
        }
    """

    machine_sequences = {
        machine_id: []
        for machine_id in machines
    }


    for job_id, operations in jobs.items():

        for operation_index, (
            machine_id,
            processing_time,
        ) in enumerate(
            operations,
            start=1,
        ):

            machine_sequences[
                machine_id
            ].append(
                (
                    job_id,
                    operation_index,
                )
            )


    # ========================================================
    # 按当前调度中的开始时间排序
    # ========================================================

    for machine_id in machines:

        machine_sequences[
            machine_id
        ].sort(
            key=lambda operation: (
                start_times[operation],
                operation[0],
                operation[1],
            )
        )


    return machine_sequences


# ============================================================
# 2. 给定 Machine Sequence，重新计算最早可行调度
# ============================================================

def decode_machine_sequences(
    jobs,
    machines,
    machine_sequences,
):
    """
    固定每台机器上的加工顺序后，
    根据：

    1. Job precedence
    2. Machine sequence

    重新计算最早开始时间。

    如果这些顺序产生有向环，则返回：

        None, None
    """

    nodes = []

    processing_time = {}


    # ========================================================
    # 建立所有工序节点
    # ========================================================

    for job_id, operations in jobs.items():

        for operation_index, (
            machine_id,
            duration,
        ) in enumerate(
            operations,
            start=1,
        ):

            node = (
                job_id,
                operation_index,
            )

            nodes.append(node)

            processing_time[
                node
            ] = duration


    # ========================================================
    # 有向图
    # ========================================================

    adjacency = {
        node: []
        for node in nodes
    }

    indegree = {
        node: 0
        for node in nodes
    }


    def add_arc(
        node_from,
        node_to,
    ):
        adjacency[
            node_from
        ].append(
            node_to
        )

        indegree[
            node_to
        ] += 1


    # ========================================================
    # 3. Job precedence arcs
    # ========================================================
    #
    # J_i1 -> J_i2 -> J_i3 -> ...
    # ========================================================

    for job_id, operations in jobs.items():

        for operation_index in range(
            1,
            len(operations),
        ):

            add_arc(
                (
                    job_id,
                    operation_index,
                ),
                (
                    job_id,
                    operation_index + 1,
                ),
            )


    # ========================================================
    # 4. Machine sequence arcs
    # ========================================================
    #
    # 如果某机器：
    #
    # A -> B -> C
    #
    # 就加入：
    #
    # A -> B
    # B -> C
    # ========================================================

    for machine_id in machines:

        sequence = (
            machine_sequences[
                machine_id
            ]
        )

        for index in range(
            len(sequence) - 1
        ):

            add_arc(
                sequence[index],
                sequence[index + 1],
            )


    # ========================================================
    # 5. Topological Sort
    # ========================================================

    ready = [
        node
        for node in nodes
        if indegree[node] == 0
    ]

    heapq.heapify(
        ready
    )


    start_times = {
        node: 0.0
        for node in nodes
    }


    processed_nodes = 0


    while ready:

        node = heapq.heappop(
            ready
        )

        processed_nodes += 1


        finish_time = (
            start_times[node]
            + processing_time[node]
        )


        for successor in adjacency[
            node
        ]:

            # --------------------------------------------
            # successor 必须等所有 predecessor 完成
            # --------------------------------------------

            start_times[
                successor
            ] = max(
                start_times[
                    successor
                ],
                finish_time,
            )


            indegree[
                successor
            ] -= 1


            if (
                indegree[
                    successor
                ]
                == 0
            ):

                heapq.heappush(
                    ready,
                    successor,
                )


    # ========================================================
    # 6. 检查是否存在 Cycle
    # ========================================================

    if processed_nodes != len(
        nodes
    ):

        return (
            None,
            None,
        )


    # ========================================================
    # 7. Makespan
    # ========================================================

    cmax_value = max(
        start_times[node]
        + processing_time[node]
        for node in nodes
    )


    return (
        start_times,
        cmax_value,
    )


# ============================================================
# 3. 计算已有 Schedule 的 Makespan
# ============================================================

def calculate_makespan(
    jobs,
    start_times,
):
    completion_times = []


    for job_id, operations in jobs.items():

        for operation_index, (
            machine_id,
            processing_time,
        ) in enumerate(
            operations,
            start=1,
        ):

            completion_times.append(
                start_times[
                    job_id,
                    operation_index,
                ]
                + processing_time
            )


    return max(
        completion_times
    )


# ============================================================
# 4. Adjacent-Swap Local Search
# ============================================================

def improve_with_adjacent_swaps(
    jobs,
    machines,
    initial_start_times,
    max_iterations=100,
):
    """
    Best-improvement adjacent-swap local search。

    每一轮：

    1. 枚举每台机器上的所有相邻工序对；
    2. 交换；
    3. 如果产生 cycle，则丢弃；
    4. 重新 decode；
    5. 找本轮 Makespan 改善最大的邻居；
    6. 接受该邻居；
    7. 直到不存在改善。
    """

    start_clock = (
        time.perf_counter()
    )


    # ========================================================
    # 1. MWKR 原始 Makespan
    # ========================================================

    input_cmax = (
        calculate_makespan(
            jobs,
            initial_start_times,
        )
    )


    # ========================================================
    # 2. 提取初始 Machine Sequence
    # ========================================================

    current_sequences = (
        build_machine_sequences(
            jobs=jobs,
            machines=machines,
            start_times=(
                initial_start_times
            ),
        )
    )


    # ========================================================
    # 3. 对固定 Machine Sequence 做 earliest-start decode
    # ========================================================

    (
        current_start_times,
        current_cmax,
    ) = decode_machine_sequences(
        jobs=jobs,
        machines=machines,
        machine_sequences=(
            current_sequences
        ),
    )


    if current_start_times is None:

        raise ValueError(
            "Initial schedule produced "
            "an invalid machine sequence."
        )


    decoded_initial_cmax = (
        current_cmax
    )


    # ========================================================
    # 4. Local Search
    # ========================================================

    iteration = 0

    evaluated_moves = 0

    feasible_moves = 0


    while (
        iteration
        < max_iterations
    ):

        best_cmax = (
            current_cmax
        )

        best_start_times = None

        best_sequences = None


        # ====================================================
        # 枚举所有机器
        # ====================================================

        for machine_id in machines:

            sequence = (
                current_sequences[
                    machine_id
                ]
            )


            # ================================================
            # 枚举所有 Adjacent Swap
            # ================================================

            for position in range(
                len(sequence) - 1
            ):

                evaluated_moves += 1


                # --------------------------------------------
                # Copy 当前 Machine Sequence
                # --------------------------------------------

                candidate_sequences = {
                    m: list(seq)
                    for m, seq
                    in current_sequences.items()
                }


                # --------------------------------------------
                # 交换相邻工序
                # --------------------------------------------

                candidate_sequences[
                    machine_id
                ][position], candidate_sequences[
                    machine_id
                ][position + 1] = (
                    candidate_sequences[
                        machine_id
                    ][position + 1],
                    candidate_sequences[
                        machine_id
                    ][position],
                )


                # --------------------------------------------
                # Decode
                # --------------------------------------------

                (
                    candidate_start_times,
                    candidate_cmax,
                ) = decode_machine_sequences(
                    jobs=jobs,
                    machines=machines,
                    machine_sequences=(
                        candidate_sequences
                    ),
                )


                # --------------------------------------------
                # Cycle -> 不可行邻居
                # --------------------------------------------

                if (
                    candidate_start_times
                    is None
                ):
                    continue


                feasible_moves += 1


                # --------------------------------------------
                # Best Improvement
                # --------------------------------------------

                if (
                    candidate_cmax
                    < best_cmax - 1e-9
                ):

                    best_cmax = (
                        candidate_cmax
                    )

                    best_start_times = (
                        candidate_start_times
                    )

                    best_sequences = (
                        candidate_sequences
                    )


        # ====================================================
        # 5. 没有更好的邻居
        # ====================================================

        if best_sequences is None:

            break


        # ====================================================
        # 6. 接受本轮最好邻居
        # ====================================================

        current_sequences = (
            best_sequences
        )

        current_start_times = (
            best_start_times
        )

        current_cmax = (
            best_cmax
        )

        iteration += 1


    # ========================================================
    # 7. Runtime
    # ========================================================

    runtime = (
        time.perf_counter()
        - start_clock
    )


    # ========================================================
    # 8. Statistics
    # ========================================================

    stats = {
        "input_cmax": (
            input_cmax
        ),
        "decoded_initial_cmax": (
            decoded_initial_cmax
        ),
        "final_cmax": (
            current_cmax
        ),
        "iterations": (
            iteration
        ),
        "evaluated_moves": (
            evaluated_moves
        ),
        "feasible_moves": (
            feasible_moves
        ),
        "runtime": (
            runtime
        ),
    }


    return (
        current_start_times,
        current_cmax,
        stats,
    )