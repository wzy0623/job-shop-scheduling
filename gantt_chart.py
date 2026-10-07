# gantt_chart.py
# ============================================================
# Job Shop Scheduling Gantt Chart
# ============================================================

from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent


def plot_gantt(
    jobs,
    machines,
    start_times,
    cmax_value,
    filename="gantt_chart.png",
    show=True,
):
    """
    绘制 Job Shop Scheduling 的 Gantt Chart。

    Parameters
    ----------
    jobs:
        Job 数据。

    machines:
        机器编号列表。

    start_times:
        {(job_id, operation_index): start_time}

    cmax_value:
        最优 Makespan。

    filename:
        保存图片的文件名。

    show:
        是否弹出图形窗口。
    """

    # ========================================================
    # 1. 创建画布
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(11, 5.5)
    )


    # ========================================================
    # 2. 为每台机器确定纵坐标
    # ========================================================

    machine_y = {
        machine_id: index
        for index, machine_id in enumerate(machines)
    }


    # ========================================================
    # 3. 使用 matplotlib 默认颜色循环
    #    同一个 Job 使用相同颜色
    # ========================================================

    color_cycle = (
        plt.rcParams["axes.prop_cycle"]
        .by_key()["color"]
    )

    job_colors = {}

    for index, job_id in enumerate(jobs):

        job_colors[job_id] = (
            color_cycle[
                index % len(color_cycle)
            ]
        )


    # ========================================================
    # 4. 绘制每一道工序
    # ========================================================

    for job_id, operations in jobs.items():

        for operation_index, (
            machine_id,
            processing_time,
        ) in enumerate(
            operations,
            start=1,
        ):

            start_time = start_times[
                job_id,
                operation_index
            ]

            y = machine_y[machine_id]

            # --------------------------------------------
            # 绘制横向时间条
            # --------------------------------------------

            ax.barh(
                y=y,
                width=processing_time,
                left=start_time,
                height=0.55,
                color=job_colors[job_id],
                edgecolor="black",
            )

            # --------------------------------------------
            # 在时间条中间写 Job / Operation
            # --------------------------------------------

            ax.text(
                start_time + processing_time / 2,
                y,
                f"J{job_id}-O{operation_index}",
                ha="center",
                va="center",
                fontsize=9,
            )


    # ========================================================
    # 5. 坐标轴
    # ========================================================

    ax.set_yticks(
        list(machine_y.values())
    )

    ax.set_yticklabels(
        [
            f"Machine {machine_id}"
            for machine_id in machines
        ]
    )

    ax.set_xlabel("Time")

    ax.set_ylabel("Machine")

    ax.set_title(
        "Job Shop Scheduling - Gantt Chart"
    )


    # ========================================================
    # 6. 标出 Makespan
    # ========================================================

    ax.axvline(
        x=cmax_value,
        linestyle="--",
        linewidth=1.5,
        label=f"Makespan = {cmax_value:.0f}",
    )


    # ========================================================
    # 7. 图形细节
    # ========================================================

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.4,
    )

    ax.set_xlim(
        0,
        cmax_value + 1,
    )

    # Machine 1 放在最上面
    ax.invert_yaxis()

    ax.legend()

    plt.tight_layout()


    # ========================================================
    # 8. 保存图片
    # ========================================================

    output_path = (
        PROJECT_DIR / filename
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    print(
        f"\nGantt Chart 已保存："
        f"{output_path}"
    )


    # ========================================================
    # 9. 是否显示
    # ========================================================

    if show:

        plt.show()

    else:

        plt.close(fig)