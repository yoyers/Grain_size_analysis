"""Core functions for grain size analysis of SEM images."""
import numpy as np
import pandas as pd
from skimage import io, segmentation, measure


def load_image(path, crop_row=708):
    """Read a SEM image and remove the info bar at the bottom."""
    img = io.imread(path)
    return img[:crop_row]


def load_model(gpu=True):
    """Load the Cellpose model once (slow step)."""
    from cellpose import models
    return models.CellposeModel(gpu=gpu)


def segment_cellpose(img, flow_threshold=0.4, cellprob_threshold=0.0,
                     gpu=True, model=None):
    """Segment grains with Cellpose. Returns a mask array: 0 = background,
    1..N = grain number. Pass a preloaded model to analyse many images."""
    if model is None:
        model = load_model(gpu)
    masks = model.eval(img, flow_threshold=flow_threshold,
                       cellprob_threshold=cellprob_threshold)[0]
    return masks


def measure_grains(masks, nm_per_pixel, min_grain_nm=100):
    """Clean the masks and measure each grain.

    Removes grains touching the border and grains smaller than min_grain_nm.
    Grains are numbered by decreasing area (1 = biggest).
    Returns (final_labels, table).
    """
    labels = segmentation.clear_border(masks)

    props = [r for r in measure.regionprops(labels)
             if r.equivalent_diameter_area * nm_per_pixel >= min_grain_nm]
    props.sort(key=lambda r: r.area, reverse=True)

    final_labels = np.zeros_like(labels)
    rows = []
    for new_id, region in enumerate(props, start=1):
        final_labels[tuple(region.coords.T)] = new_id
        cy, cx = region.centroid
        rows.append({
            "grain_id": new_id,
            "diameter_nm": region.equivalent_diameter_area * nm_per_pixel,
            "area_nm2": region.area * nm_per_pixel**2,
            "major_nm": region.major_axis_length * nm_per_pixel,
            "minor_nm": region.minor_axis_length * nm_per_pixel,
            "aspect_ratio": region.major_axis_length / region.minor_axis_length,
            "centroid_x_px": cx,
            "centroid_y_px": cy,
        })

    return final_labels, pd.DataFrame(rows)


def get_boundaries(final_labels):
    """Boolean array, True on the 1-pixel boundaries between grains."""
    return segmentation.find_boundaries(final_labels, mode="inner")