import spatialdata as sd
from sopa.io import explorer
import yaml

# TODO: Create config and combine with rest for yaml
sdata = sd.read_zarr("/scratch/1305732956.zarr")

explorer.write(
    "/results/merscope_xenium_explorer/",
    sdata,
    image_key="DAPI",
    shapes_key="sis_seg",
    points_key="transcripts",
    gene_column="gene",
    lazy=True,
    ram_threshold_gb=16,
)
