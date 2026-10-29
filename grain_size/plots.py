"""Output functions: images, CSV and Origin matrices."""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .analysis import get_boundaries


def plot_size_map(final_labels, df, title=""):
    """Grains colored by diameter, black boundaries."""
    boundaries = get_boundaries(final_labels)

    lookup = np.concatenate([[np.nan], df["diameter_nm"].values])
    diam_map = lookup[final_labels]

    black = np.zeros(final_labels.shape + (4,))
    black[boundaries] = (0, 0, 0, 1)

    cmap = plt.cm.viridis.copy()
    cmap.set_bad("white")

    fig, ax = plt.subplots(figsize=(12, 9))
    im = ax.imshow(diam_map, cmap=cmap)
    ax.imshow(black)
    ax.axis("off")
    fig.colorbar(im, ax=ax, shrink=0.8).set_label("Equivalent diameter (nm)")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_numbered(img, final_labels, df, title="", fontsize=6):
    """SEM image with semitransparent boundaries and grain numbers."""
    boundaries = get_boundaries(final_labels)

    red = np.zeros(final_labels.shape + (4,))
    red[boundaries] = (1, 0, 0, 0.5)

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.imshow(img, cmap="gray")
    ax.imshow(red)
    ax.axis("off")
    for _, row in df.iterrows():
        ax.text(row["centroid_x_px"], row["centroid_y_px"],
                str(int(row["grain_id"])), color="yellow",
                fontsize=fontsize, ha="center", va="center")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def origin_matrices(final_labels, df):
    """Two matrices for Origin: diameter per pixel and grain_id per pixel."""
    boundaries = get_boundaries(final_labels)

    diam_matrix = np.full(final_labels.shape, np.nan)
    mask = final_labels > 0
    diam_matrix[mask] = df["diameter_nm"].values[final_labels[mask] - 1]
    diam_matrix[boundaries] = 0

    return diam_matrix, final_labels.copy()


def save_results(img, final_labels, df, out_dir, stem, dpi=300):
    """Save everything for one image into out_dir."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / f"{stem}_grains_numbered.csv", index=False)

    fig = plot_size_map(final_labels, df, f"{stem}: grain size map")
    fig.savefig(out_dir / f"{stem}_size_map.png", dpi=dpi)
    plt.close(fig)

    fig = plot_numbered(img, final_labels, df, f"{stem}: grain numbers")
    fig.savefig(out_dir / f"{stem}_numbered.png", dpi=dpi)
    plt.close(fig)

    diam_matrix, id_matrix = origin_matrices(final_labels, df)
    pd.DataFrame(diam_matrix).to_csv(
        out_dir / f"{stem}_origin_diameter_matrix.csv",
        header=False, index=False, na_rep="")
    pd.DataFrame(id_matrix).to_csv(
        out_dir / f"{stem}_origin_id_matrix.csv",
        header=False, index=False)