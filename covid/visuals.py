"""Visualization functions"""

import os

import matplotlib
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import colorConverter as cc
from matplotlib.lines import Line2D

from covid.config import MAX_X, MAX_Y, MIN_X, MIN_Y, data_path


def plot_mean_and_ci(mean, lb, ub, color_mean=None, color_shading=None):
    # plot the shaded range of the confidence intervals
    plt.fill_between(range(mean.shape[0]), ub, lb, color=color_shading, alpha=0.5)
    # plot the mean on top
    plt.plot(mean, color_mean)


class LegendObject(object):
    """
    from: https://studywolf.wordpress.com/2017/11/21/matplotlib-legends-for-mean-and-confidence-interval-plots/
    """

    def __init__(self, facecolor="red", edgecolor="white", dashed=False):
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.dashed = dashed

    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width, height = handlebox.width, handlebox.height
        patch = mpatches.Rectangle(
            # create a rectangle that is filled with color
            [x0, y0],
            width,
            height,
            facecolor=self.facecolor,
            # and whose edges are the faded color
            edgecolor=self.edgecolor,
            lw=3,
        )
        handlebox.add_artist(patch)

        # if we're creating the legend for a dashed line,
        # manually add the dash in to our rectangle
        if self.dashed:
            patch1 = mpatches.Rectangle(
                [x0 + 2 * width / 5, y0],
                width / 5,
                height,
                facecolor=self.edgecolor,
                transform=handlebox.get_transform(),
            )
            handlebox.add_artist(patch1)

        return patch


def plot_curve(df):
    bg = np.array([1, 1, 1])  # background of the legend is white
    colors = ["black", "red", "green", "blue", "purple"]
    cols = ["dead", "infected", "immune", "total", "susceptible"]
    data_color_map = dict(zip(cols, colors))
    # with alpha = .5, the faded color is the average of the background and color
    colors_faded = [(np.array(cc.to_rgb(color)) + bg) / 2.0 for color in colors]

    fig = plt.figure(1, figsize=(7, 4))

    def get_mean_bounds(df, col):
        mean = df[f"{col} mean"]
        std = df[f"{col} std"]
        return mean, mean + std, mean - std

    for col, color in data_color_map.items():
        mu, ub, lb = get_mean_bounds(df, col)
        plot_mean_and_ci(mu, ub, lb, color_mean=color, color_shading=color)

    handler_map = {
        i: LegendObject(colors[i], colors_faded[i]) for i in range(len(colors))
    }

    plt.legend([i for i in range(len(colors))], cols, handler_map=handler_map)
    plt.xlabel("time (days)")
    plt.ylabel("num people")
    plt.tight_layout()
    plt.grid()
    plt.show()


def augment(arr, numsteps):
    xold, yold = arr[0], arr[1]
    xnew = []
    ynew = []
    for i in range(len(xold) - 1):
        x_steps = (xold[i + 1] - xold[i]) / numsteps
        y_steps = (yold[i + 1] - yold[i]) / numsteps
        for s in range(numsteps):
            xnew = np.append(xnew, xold[i] + s * x_steps)
            ynew = np.append(ynew, yold[i] + s * y_steps)
    return np.array([xnew, ynew])


def create_animation(all_steps_lst, total_frames=400, fps=20, **kwargs):
    Writer = animation.writers["ffmpeg"]
    writer = Writer(fps=fps, metadata=dict(artist="Me"), bitrate=1800)
    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.set_xlim([MIN_X, MAX_X])
    ax.set_ylim([MIN_Y, MAX_Y])
    plt.title("Title", fontsize=20)

    def _plot_group(ser, ax, *args, **kwargs):
        if ser.size >= 2:
            ax.plot(ser[0], ser[1], *args, **kwargs)

    def plot_points(i):
        alpha = 0.7
        plt.cla()
        dct = all_steps_lst[i]
        _plot_group(dct["dead"], ax, marker="o", color="black", linestyle="", alpha=alpha)
        _plot_group(
            dct["infected"], ax, marker="o", color="red", linestyle="", alpha=alpha
        )
        _plot_group(
            dct["immune"], ax, marker="o", color="green", linestyle="", alpha=alpha
        )
        _plot_group(
            dct["susceptible"], ax, marker="o", color="purple", linestyle="", alpha=alpha
        )
        ax.set_xlim([MIN_X, MAX_X])
        ax.set_ylim([MIN_Y, MAX_Y])
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])

        custom_lines = [Line2D([0], [0], color="purple", lw=4, alpha=alpha),
                        Line2D([0], [0], color="red", lw=4, alpha=alpha),
                        Line2D([0], [0], color="green", lw=4, alpha=alpha),
                        Line2D([0], [0], color="black", lw=4, alpha=alpha)]

        ax.legend(custom_lines, ['Susceptible', 'Infected', 'Recovered', 'Dead'], loc='upper right',
                  bbox_to_anchor=(1, 1))
        # ax.legend(loc='upper right', bbox_to_anchor=(0, 0))#, ncol=4, numpoints=1)

    ani = matplotlib.animation.FuncAnimation(
        fig, plot_points, frames=total_frames, repeat=True
    )
    output_file = kwargs.get(
        "output_file", os.path.join(data_path, "covid_interactions.mp4")
    )
    ani.save(output_file, writer=writer)
