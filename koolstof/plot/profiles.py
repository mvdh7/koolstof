import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
from sklearn import cluster


def get_cluster_profile(x, y, data=None, cluster_bandwidth=5, linspace_num=100):
    """Get clusters from input data and interpolate them."""
    # Extract data from data, if required
    if data is not None:
        x = data[x]
        y = data[y]
    # Eliminate NaNs from input data
    l = ~np.isnan(x) & ~np.isnan(y)
    dx = x[l]
    dy = y[l]
    # Do MeanShift clustering of the x-variable
    ms = cluster.MeanShift(bandwidth=cluster_bandwidth)
    ms.fit(np.vstack(dx))
    # Get y-variable values at x-variable cluster centres
    cn = ms.labels_.ravel()
    cx = ms.cluster_centers_.ravel()
    cy = np.full_like(cx, np.nan)
    for i in range(len(cy)):
        cy[i] = np.mean(dy[cn == i])
    # Sort clusters
    ci = np.argsort(cx)
    cx = cx[ci]
    cy = cy[ci]
    # Generate PCHIP interpolation of clustered data
    px = np.linspace(np.min(cx), np.max(cx), num=linspace_num)
    py = interpolate.pchip(cx, cy)(px)
    return px, py, cx, cy, cn


def cluster_profile(
    x,
    y,
    data=None,
    ax=None,
    cluster_bandwidth=5,
    linspace_num=100,
    invert_xy=False,
    plot_kwargs=None,
    scatter_kwargs=None,
):
    """Get clusters from input data, interpolate them and plot the results."""
    # Extract data from data, if required
    if data is not None:
        x = data[x]
        y = data[y]
    p_xy = get_cluster_profile(
        x,
        y,
        cluster_bandwidth=cluster_bandwidth,
        linspace_num=linspace_num,
    )[:2]
    if ax is None:
        _, ax = plt.subplots()
    if plot_kwargs is None:
        plot_kwargs = {}
    if scatter_kwargs is None:
        scatter_kwargs = {}
    xy = (x, y)
    if invert_xy:
        p_xy = p_xy[::-1]
        xy = xy[::-1]
    ax_plot = ax.plot(*p_xy, **plot_kwargs)
    ax_scatter = ax.scatter(*xy, **scatter_kwargs)
    return ax, ax_plot, ax_scatter
