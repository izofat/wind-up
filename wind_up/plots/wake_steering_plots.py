import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from wind_up.constants import SCATTER_ALPHA, SCATTER_S
from wind_up.math_funcs import circ_diff
from wind_up.models import PlotConfig


def plot_yaw_direction_pre_post(
    pre_df: pd.DataFrame,
    post_df: pd.DataFrame,
    *,
    test_name: str,
    ref_name: str,
    ref_ws_col: str,
    ref_wd_col: str,
    plot_cfg: PlotConfig,
) -> None:
    pre_df = pre_df.copy()
    post_df = post_df.copy()

    test_wd_col = "test_YawAngleMean"
    toggle_name = "wake steering"

    pre_df["yaw_offset"] = circ_diff(pre_df[ref_wd_col], pre_df[test_wd_col])
    post_df["yaw_offset"] = circ_diff(post_df[ref_wd_col], post_df[test_wd_col])

    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.scatter(
        pre_df[ref_wd_col],
        pre_df[test_wd_col],
        s=SCATTER_S,
        alpha=SCATTER_ALPHA,
        label=f"{toggle_name} OFF",
    )
    plt.scatter(
        post_df[ref_wd_col],
        post_df[test_wd_col],
        s=SCATTER_S,
        alpha=SCATTER_ALPHA,
        label=f"{toggle_name} ON",
    )
    plt.xlabel(f"{ref_wd_col} [deg]")
    plt.ylabel(f"{test_wd_col} [deg]")
    plt.grid()
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.scatter(
        pre_df[ref_wd_col],
        pre_df["yaw_offset"],
        s=SCATTER_S,
        alpha=SCATTER_ALPHA,
        label=f"{toggle_name} OFF",
    )
    plt.scatter(
        post_df[ref_wd_col],
        post_df["yaw_offset"],
        s=SCATTER_S,
        alpha=SCATTER_ALPHA,
        label=f"{toggle_name} ON",
    )
    plt.xlabel(f"{ref_wd_col} [deg]")
    plt.ylabel(f"{test_wd_col} - {ref_wd_col} [deg]")
    plt.grid()

    plot_title = f"{ref_name} and {test_name} yaw direction by {toggle_name} toggle"
    plt.suptitle(plot_title)
    if plot_cfg.show_plots:
        plt.show()
    if plot_cfg.save_plots:
        (plot_cfg.plots_dir / test_name / "wake_steering").mkdir(exist_ok=True)
        plt.savefig(plot_cfg.plots_dir / test_name / "wake_steering" / f"{plot_title}.png")
    plt.close()

    ws_bin_width = 2
    wd_bin_width = 5

    ws_bin_edges = np.arange(0, pre_df[ref_ws_col].max() + ws_bin_width, ws_bin_width)
    pre_df["ws_bins"] = pd.cut(pre_df[ref_ws_col], bins=ws_bin_edges, retbins=False)
    pre_df["ws_bin_centre"] = [x.mid for x in pre_df["ws_bins"]]
    post_df["ws_bins"] = pd.cut(post_df[ref_ws_col], bins=ws_bin_edges, retbins=False)
    post_df["ws_bin_centre"] = [x.mid for x in post_df["ws_bins"]]

    wd_bin_edges = np.arange(0, pre_df[ref_wd_col].max() + wd_bin_width, wd_bin_width)
    pre_df["wd_bins"] = pd.cut(pre_df[ref_wd_col], bins=wd_bin_edges, retbins=False)
    pre_df["wd_bin_centre"] = [x.mid for x in pre_df["wd_bins"]]
    post_df["wd_bins"] = pd.cut(post_df[ref_wd_col], bins=wd_bin_edges, retbins=False)
    post_df["wd_bin_centre"] = [x.mid for x in post_df["wd_bins"]]

    for tgl in [0, 1]:
        on_or_off = "OFF" if tgl == 0 else "ON"
        plot_df = pre_df if tgl == 0 else post_df
        plt.figure(figsize=(8, 8))
        plt.subplot(2, 1, 1)
        sns.heatmap(
            plot_df.pivot_table(
                index="ws_bin_centre",
                columns="wd_bin_centre",
                values="yaw_offset",
                aggfunc=lambda x: x.count() / 6,
            )[::-1],
            annot=True,
            cmap="gray_r",
            fmt=".1f",
            linewidths=0.5,
            cbar_kws={"label": "hours of data"},
        )
        plt.xlabel("wind direction bin centre [deg]")
        plt.ylabel("wind speed bin centre [m/s]")

        plt.subplot(2, 1, 2)
        sns.heatmap(
            plot_df.pivot_table(index="ws_bin_centre", columns="wd_bin_centre", values="yaw_offset")[::-1],
            annot=True,
            cmap="YlGnBu",
            fmt=".1f",
            linewidths=0.5,
            vmin=0,
            vmax=20,
            cbar_kws={"label": "yaw offset [deg]"},
        )

        plt.xlabel("wind direction bin centre [deg]")
        plt.ylabel("wind speed bin centre [m/s]")

        plot_title = f"{ref_name} minus {test_name} yaw direction vs ws and wd toggle {on_or_off}"
        plt.suptitle(plot_title)
        plt.tight_layout()
        if plot_cfg.show_plots:
            plt.show()
        if plot_cfg.save_plots:
            (plot_cfg.plots_dir / test_name / "wake_steering").mkdir(exist_ok=True)
            plt.savefig(plot_cfg.plots_dir / test_name / "wake_steering" / f"{plot_title}.png")
        plt.close()
