import spatialdata as sd
from sopa.io import explorer
import yaml

# TODO: Create config and combine with rest for yaml
sdata = sd.read_zarr("/data/130573295_spatialdata/130573295_mip_dapi.zarr")

explorer.write(
    "/results/merscope_xenium_explorer/",
    sdata,
    image_key="max_z_layers",
    shapes_key="sis_cell_polygons",
    points_key="segmented_spot_table",
    table_key="cell_by_gene",
    gene_column="gene",
    lazy=True,
    ram_threshold_gb=16,
)
