# tabu_search.py
# ============================================================
# Job Shop Scheduling
# Basic Adjacent-Swap Tabu Search
# ============================================================

import time

from local_search import (
    build_machine_sequences,
    decode_machine_sequences,
    calculate_makespan,
)


def tabu_search(
    jobs,
    machines,
    initial_start_times,
    max_iterations=100,
    tabu_tenure=7,
):
    """
    使用 Adjacent-Swap Tabu Search 改善一个初始 JSSP 调度。

    基本流程：
    1. 从初始调度提取 Machine Sequence；
    2. 枚举所有相邻交换；
    3. 允许选择比当前解更差的邻居；
    4. 使用 Tabu List 防止立即反向交换；
    5. 如果 tabu move 能创造历史最好解，则允许执行；
    6. 始终记录全局最好解。

    Parameters
    ----------
    jobs:
        Job 数据。

    machines:
        Machine 编号。

    initial_start_times:
        初始可行调度。

    max_iterations:
        最大迭代次数。

    tabu_tenure:
        一个 move 保持 tabu 的迭代轮数。

    Returns
    -------
    best_start_times:
        找到的最好调度。

    best_cmax:
        最好 Makespan。

    stats:
        搜索统计信息。
    """

    start_clock = time.perf_counter()


    # ========================================================
    # 1. 初始 Makespan
    # ========================================================

    input_cmax = calculate_makespan(
        jobs,
        initial_start_times,
    )


    # ========================================================
    # 2. 提取初始 Machine Sequence
    # ========================================================

    current_sequences = (
        build_machine_sequences(
            jobs=jobs,
            machines=machines,
            start_times=initial_start_times,
        )
    )


    # ========================================================
    # 3. Decode
    # ========================================================

    (
        current_start_times,
        current_cmax,
    ) = decode_machine_sequences(
        jobs=jobs,
        machines=machines,
        machine_sequences=current_sequences,
    )


    if current_start_times is None:

        raise ValueError(
            "Initial schedule produced "
            "an invalid machine sequence."
        )


    # ========================================================
    # 4. Global Best
    # ========================================================

    best_sequences = {
        machine_id: list(sequence)
        for machine_id, sequence
        in current_sequences.items()
    }

    best_start_times = dict(
        current_start_times
    )

    best_cmax = current_cmax


    # ========================================================
    # 5. Tabu List
    # ========================================================
    #
    # tabu_until[move] = iteration
    #
    # move:
    #
    # (
    #     machine_id,
    #     operation_a,
    #     operation_b
    # )
    #
    # operation_a / b:
    #
    # (job_id, operation_index)
    # ========================================================

    tabu_until = {}


    # ========================================================
    # 6. Statistics
    # ========================================================

    evaluated_moves = 0
    feasible_moves = 0
    tabu_skipped = 0
    aspiration_uses = 0

    accepted_worsening_moves = 0
    accepted_equal_moves = 0

    best_improvements = 0


    # ========================================================
    # 7. Main Tabu Search Loop
    # ========================================================

    completed_iterations = 0


    for iteration in range(
        1,
        max_iterations + 1,
    ):

        best_candidate = None


        # ====================================================
        # 枚举所有 Machine
        # ====================================================

        for machine_id in machines:

            sequence = (
                current_sequences[
                    machine_id
                ]
            )


            # =================================================
            # 枚举 Adjacent Swap
            # =================================================

            for position in range(
                len(sequence) - 1
            ):

                evaluated_moves += 1


                operation_a = (
                    sequence[position]
                )

                operation_b = (
                    sequence[
                        position + 1
                    ]
                )


                # --------------------------------------------
                # 用排序后的 pair 表示 move
                #
                # 这样：
                #
                # A <-> B
                #
                # 和：
                #
                # B <-> A
                #
                # 被视为同一个 tabu move。
                # --------------------------------------------

                ordered_pair = tuple(
                    sorted(
                        [
                            operation_a,
                            operation_b,
                        ]
                    )
                )


                move_key = (
                    machine_id,
                    ordered_pair[0],
                    ordered_pair[1],
                )


                # --------------------------------------------
                # 构造 Candidate Sequence
                # --------------------------------------------

                candidate_sequences = {
                    m: list(seq)
                    for m, seq
                    in current_sequences.items()
                }


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
                # Decode Candidate
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
                # Cycle -> 不可行
                # --------------------------------------------

                if candidate_start_times is None:

                    continue


                feasible_moves += 1


                # --------------------------------------------
                # Tabu Check
                # --------------------------------------------

                is_tabu = (
                    move_key in tabu_until
                    and
                    iteration
                    <= tabu_until[
                        move_key
                    ]
                )


                # --------------------------------------------
                # Aspiration
                #
                # 如果它能创造历史最好解，
                # 即使 tabu 也允许。
                # --------------------------------------------

                aspiration = (
                    candidate_cmax
                    < best_cmax - 1e-9
                )


                if is_tabu and not aspiration:

                    tabu_skipped += 1

                    continue


                if is_tabu and aspiration:

                    aspiration_uses += 1


                # --------------------------------------------
                # 选择允许邻居中 Makespan 最小的
                #
                # 注意：
                #
                # 它可以比 current_cmax 更差。
                # --------------------------------------------

                if (
                    best_candidate is None
                    or
                    candidate_cmax
                    < best_candidate[
                        "cmax"
                    ] - 1e-9
                ):

                    best_candidate = {
                        "cmax": (
                            candidate_cmax
                        ),
                        "start_times": (
                            candidate_start_times
                        ),
                        "sequences": (
                            candidate_sequences
                        ),
                        "move_key": (
                            move_key
                        ),
                    }


        # ====================================================
        # 没有允许的可行邻居
        # ====================================================

        if best_candidate is None:

            break


        old_current_cmax = (
            current_cmax
        )


        # ====================================================
        # 接受 Candidate
        #
        # 即使它比当前解更差，也接受。
        # ====================================================

        current_sequences = (
            best_candidate[
                "sequences"
            ]
        )

        current_start_times = (
            best_candidate[
                "start_times"
            ]
        )

        current_cmax = (
            best_candidate[
                "cmax"
            ]
        )


        # ====================================================
        # 记录 Move 为 Tabu
        # ====================================================

        tabu_until[
            best_candidate[
                "move_key"
            ]
        ] = (
            iteration
            + tabu_tenure
        )


        # ====================================================
        # 统计接受了什么类型的 move
        # ====================================================

        if (
            current_cmax
            > old_current_cmax + 1e-9
        ):

            accepted_worsening_moves += 1

        elif (
            abs(
                current_cmax
                - old_current_cmax
            )
            <= 1e-9
        ):

            accepted_equal_moves += 1


        # ====================================================
        # 更新 Global Best
        # ====================================================

        if (
            current_cmax
            < best_cmax - 1e-9
        ):

            best_cmax = (
                current_cmax
            )

            best_start_times = dict(
                current_start_times
            )

            best_sequences = {
                machine_id: list(
                    sequence
                )
                for (
                    machine_id,
                    sequence,
                ) in current_sequences.items()
            }

            best_improvements += 1


        completed_iterations = (
            iteration
        )


        # ====================================================
        # 清理已经过期的 tabu entries
        # ====================================================

        expired_moves = [
            move
            for move, until
            in tabu_until.items()
            if until < iteration
        ]


        for move in expired_moves:

            del tabu_until[move]


    # ========================================================
    # 8. Runtime
    # ========================================================

    runtime = (
        time.perf_counter()
        - start_clock
    )


    # ========================================================
    # 9. Statistics
    # ========================================================

    stats = {
        "input_cmax": input_cmax,
        "decoded_initial_cmax": (
            calculate_makespan(
                jobs,
                best_start_times,
            )
            if completed_iterations == 0
            else None
        ),
        "best_cmax": best_cmax,
        "final_current_cmax": (
            current_cmax
        ),
        "iterations": (
            completed_iterations
        ),
        "tabu_tenure": (
            tabu_tenure
        ),
        "evaluated_moves": (
            evaluated_moves
        ),
        "feasible_moves": (
            feasible_moves
        ),
        "tabu_skipped": (
            tabu_skipped
        ),
        "aspiration_uses": (
            aspiration_uses
        ),
        "accepted_worsening_moves": (
            accepted_worsening_moves
        ),
        "accepted_equal_moves": (
            accepted_equal_moves
        ),
        "best_improvements": (
            best_improvements
        ),
        "runtime": runtime,
    }


    return (
        best_start_times,
        best_cmax,
        stats,
    )