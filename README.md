# Grain size analysis for perovskite SEM images

Automatic grain segmentation with [Cellpose](https://github.com/MouseLand/cellpose)
and measurement of grain size from SEM images. Runs on Google Colab, so no
installation and no GPU are needed on your computer.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yoyers/Grain_size_analysis/blob/main/notebooks/grain_size_colab.ipynb)

## What it does

For every image in a folder it produces:

| File | Content |
|---|---|
| `<image>_size_map.png` | Grains colored by diameter, black boundaries |
| `<image>_numbered.png` | SEM image with semitransparent boundaries and grain numbers |
| `<image>_grains_numbered.csv` | One row per grain; `grain_id` matches the numbers in the image (1 = biggest) |
| `<image>_origin_*_matrix.csv` | Pixel matrices to plot and recolor in OriginLab |
| `summary_all_images.csv` | Grain count, mean, median and std for each image |
| `grains_all_images.csv` | All grains of all images in one table |

## How to use (Google Colab)

1. Put your SEM images in one folder in your Google Drive.
2. Click the **Open in Colab** badge above.
3. Select a GPU: `Runtime → Change runtime type → T4 GPU`.
4. Run Cell 1 (installs the code).
5. In Cell 2, set the path to your image folder, the output folder and
   `nm_per_pixel`, then run it.
6. Run Cell 3. Results are saved in the output folder.

### Settings

| Parameter | Meaning |
|---|---|
| `nm_per_pixel` | Pixel size, from the SEM metadata or the scale bar |
| `crop_row` | Number of rows to keep; removes the info bar at the bottom |
| `min_grain_nm` | Grains with a smaller equivalent diameter are discarded |
| `flow_threshold` | Cellpose: higher accepts more irregular shapes |
| `cellprob_threshold` | Cellpose: lower finds more/larger grains, higher finds fewer/smaller |

## How the measurement works

- Grains are segmented with Cellpose (default model).
- Grains touching the image border are removed, because they are cut off.
- Diameter is the equivalent diameter: the diameter of a circle with the same
  area as the grain.

## Local use

```
git clone https://github.com/yoyers/Grain_size_analysis.git
cd Grain_size_analysis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Cellpose is slow without a GPU. See `grain_size/analysis.py` and
`grain_size/plots.py` for the functions.

## Limitations

- Always check the overlay visually; automatic segmentation can merge or
  split some grains.
- All images in one run share the same `nm_per_pixel` and `crop_row`.

## License

MIT