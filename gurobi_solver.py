# gurobi_solver.py
# ============================================================
# Job Shop Scheduling - Gurobi MILP Solver
# ============================================================

from gurobipy import Model, GRB


def solve_job_shop(
    jobs,
    machines,
    big_m,
    verbose=False,
    return_stats=False,
    time_limit=None,
):
    """
    使用 Gurobi 求解 Job Shop Scheduling。

    Parameters
    ----------
    jobs:
        {
            job_id: [
                (machine_id, processing_time),
                ...
            ]
        }

    machines:
        Machine 编号列表。

    big_m:
        Big-M 常数。

    verbose:
        是否显示 Gurobi 日志。

    return_stats:
        是否返回求解统计信息。

    time_limit:
        最大求解时间（秒）。
        None 表示不设置时间上限。

    Returns
    -------
    默认：
        start_times, cmax_value

    return_stats=True：
        start_times, cmax_value, stats

    注意：
    即使状态为 TIME_LIMIT，
    只要 Gurobi 已找到可行解，
    仍然返回当前最好 incumbent。
    """

    # ========================================================
    # 1. 创建模型
    # ========================================================

    model = Model(
        "job_shop_scheduling"
    )

    model.Params.OutputFlag = (
        1 if verbose else 0
    )

    if time_limit is not None:

        model.Params.TimeLimit = (
            time_limit
        )


    # ========================================================
    # 2. 开始时间变量
    # ========================================================

    start = {}

    for job_id, operations in jobs.items():

        for operation_index in range(
            1,
            len(operations) + 1,
        ):

            start[
                job_id,
                operation_index,
            ] = model.addVar(
                lb=0.0,
                vtype=GRB.CONTINUOUS,
                name=(
                    f"S_"
                    f"{job_id}_"
                    f"{operation_index}"
                ),
            )


    # ========================================================
    # 3. Makespan
    # ========================================================

    cmax = model.addVar(
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="Cmax",
    )


    # ========================================================
    # 4. Job precedence constraints
    # ========================================================

    for job_id, operations in jobs.items():

        for operation_index in range(
            1,
            len(operations),
        ):

            processing_time = (
                operations[
                    operation_index - 1
                ][1]
            )

            model.addConstr(
                start[
                    job_id,
                    operation_index + 1,
                ]
                >=
                start[
                    job_id,
                    operation_index,
                ]
                + processing_time,

                name=(
                    f"precedence_"
                    f"{job_id}_"
                    f"{operation_index}"
                ),
            )


    # ========================================================
    # 5. 收集每台机器上的工序
    # ========================================================

    machine_operations = {
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

            machine_operations[
                machine_id
            ].append(
                (
                    job_id,
                    operation_index,
                    processing_time,
                )
            )


    # ========================================================
    # 6. Machine non-overlap
    # ========================================================

    for machine_id in machines:

        operations = (
            machine_operations[
                machine_id
            ]
        )

        for i in range(
            len(operations)
        ):

            for j in range(
                i + 1,
                len(operations),
            ):

                (
                    job_a,
                    op_a,
                    p_a,
                ) = operations[i]

                (
                    job_b,
                    op_b,
                    p_b,
                ) = operations[j]


                y = model.addVar(
                    vtype=GRB.BINARY,
                    name=(
                        f"y_"
                        f"{job_a}_{op_a}_"
                        f"{job_b}_{op_b}"
                    ),
                )


                # y = 1:
                # A before B

                model.addConstr(
                    start[
                        job_b,
                        op_b,
                    ]
                    >=
                    start[
                        job_a,
                        op_a,
                    ]
                    + p_a
                    - big_m * (1 - y)
                )


                # y = 0:
                # B before A

                model.addConstr(
                    start[
                        job_a,
                        op_a,
                    ]
                    >=
                    start[
                        job_b,
                        op_b,
                    ]
                    + p_b
                    - big_m * y
                )


    # ========================================================
    # 7. Makespan constraints
    # ========================================================

    for job_id, operations in jobs.items():

        last_operation_index = (
            len(operations)
        )

        last_processing_time = (
            operations[-1][1]
        )

        model.addConstr(
            cmax
            >=
            start[
                job_id,
                last_operation_index,
            ]
            + last_processing_time
        )


    # ========================================================
    # 8. Objective
    # ========================================================

    model.setObjective(
        cmax,
        GRB.MINIMIZE,
    )


    # ========================================================
    # 9. Optimize
    # ========================================================

    model.optimize()


    # ========================================================
    # 10. Status
    # ========================================================

    status_names = {
        GRB.OPTIMAL: "OPTIMAL",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
    }

    status_name = (
        status_names.get(
            model.Status,
            f"STATUS_{model.Status}",
        )
    )


    # ========================================================
    # 11. 基础统计
    # ========================================================

    solution_count = (
        model.SolCount
    )

    stats = {
        "status": status_name,
        "runtime": model.Runtime,
        "num_variables": model.NumVars,
        "num_constraints": (
            model.NumConstrs
        ),
        "solution_count": (
            solution_count
        ),
        "node_count": (
            model.NodeCount
        ),
        "incumbent": None,
        "best_bound": None,
        "mip_gap": None,
    }


    # ========================================================
    # 12. Best Bound
    # ========================================================
    #
    # 对最小化问题：
    #
    # Best Bound <= OPT <= Incumbent
    # ========================================================

    if model.Status in (
        GRB.OPTIMAL,
        GRB.TIME_LIMIT,
    ):

        stats["best_bound"] = (
            model.ObjBound
        )


    # ========================================================
    # 13. 如果已经找到可行解
    # ========================================================

    if solution_count > 0:

        stats["incumbent"] = (
            model.ObjVal
        )

        stats["mip_gap"] = (
            model.MIPGap
        )


        # ----------------------------------------------------
        # 提取当前最好可行调度
        # ----------------------------------------------------

        start_times = {}

        for (
            job_id,
            operations,
        ) in jobs.items():

            for operation_index in range(
                1,
                len(operations) + 1,
            ):

                start_times[
                    job_id,
                    operation_index,
                ] = start[
                    job_id,
                    operation_index,
                ].X


        cmax_value = (
            model.ObjVal
        )


        if return_stats:

            return (
                start_times,
                cmax_value,
                stats,
            )


        return (
            start_times,
            cmax_value,
        )


    # ========================================================
    # 14. 没有找到任何可行解
    # ========================================================

    if return_stats:

        return (
            None,
            None,
            stats,
        )

    return (
        None,
        None,
    )