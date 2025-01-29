from rioxarray import open_rasterio
from xarray import concat
from typing import Literal
from pathlib import Path
from spatialdata.models import Image2DModel, Image3DModel
from xarray import DataTree
# Note, just use the normal sopa functions if you can fit all the stains in memory.


def read_merscope_stain_imagestack(
    path: Path | str,
    stain: str,
    z: list[int] | int | None = None,
    agg_z: Literal["max", "mean"] | None = None,
    chunk_size: tuple[int] = (1, 4096, 4096),
    scale_factors: tuple[int] = (2, 2, 2, 2),
) -> DataTree:
    """
    Read in image stack for a particular stain.
    You can read in a single or multiple layers using the z parameter.
    You can aggregate layers using the agg_z parameters.

    Parameters:
    path : {str, pathlib.Path}
        path to the image.
    stain : str
        stain name i.e. DAPI or PolyT. Needs to match the file name in image directory.
    z : {int or list of ints, or None}
        Name of the exact z layers you want to extract. i.e. 0 | [0,3,6].
        If agg_z is not None, then z must be None.
    agg_z: {"max", "mean", or None}
        Aggregation function across z_planes. Will either take the maximum or minimum values of z. Max is equivalent to MIP.
    chunk_size : {tuple of ints}, optional
        Size of chunks for xarray data (which is a dask.Array). See dask documentation for more info.
    scale_factors : {tuple of ints}, optional
        Scaling factor for image across levels. i.e. (2, 2) is 2x less resolution and then 4x less resolution. Or (2, 2, 2) is 2x, then 4x, 8x less resolution.
        Does not work for multiple z_planes.
    Returns:
    im : {xarray.DataArray or xarray.DataTree}
        Either an 3D imagestack (DataTree) or an 2D image (DataArray)
        im.data property will probably be a dask array that may or may not need to be computed when writing to memory.
    """
    if (z is None) & (agg_z is None):
        return KeyError("Either z or agg_z needs to be not None")

    if (z is not None) & (agg_z is not None):
        return ValueError(
            "z and agg_z can not be both not None, select either a value for z or agg_z"
        )

    if type(path) is not Path:
        path = Path(path)

    if z:
        if type(z) is not list:
            z = [z]
        tif_paths = [path / f"mosaic_{stain}_z{z_i}.tif" for z_i in z]
    else:
        tif_paths = list(path.glob(f"mosaic_{stain}_z*.tif"))

    print(tif_paths)
    im = concat(
        [
            open_rasterio(tif_path, chunks=chunk_size).rename({"band": "z"})
            for tif_path in tif_paths
        ],
        dim="z",
    )

    # Aggregate or wrangle data for image parsing.
    if agg_z:
        if agg_z == "max":
            im = im.max(dim="z")
        elif agg_z == "mean":
            im = im.mean(dim="z")
        else:
            return KeyError(f"{agg_z} not implemented")
        im = im.expand_dims(dim="c", axis=0)
        return Image2DModel.parse(
            data=im,
            dims=("c", "y", "x"),
            c_coords=[stain],
            rgb=None,
            scale_factors=scale_factors,
        )
    elif len(z) == 1:
        im = im.max(dim="z")  # Will just pick the single z plane
        im = im.expand_dims(dim="c", axis=0)
        return Image2DModel.parse(
            data=im,
            dims=("c", "y", "x"),
            c_coords=[stain],
            rgb=None,
            scale_factors=scale_factors,
        )
    else:
        if scale_factors is not None:
            print("Multiple Z - planes not supported")
        else:
            im = im.expand_dims(dim="c", axis=0)
            return Image3DModel.parse(
                data=im,
                dims=("c", "z", "y", "x"),
                c_coords=[stain],
                rgb=None,
                scale_factors=scale_factors,
            )


# TODO: fix scale factors at some point.

# test
config = {
    "input_path": "/data/1305732956/region_0/",
    "image": {
        "stain": "DAPI",
        "z": [3, 4],
        "agg_z": None,
        "chunk_size": (1, 4096, 4096),
        "scale_factors": [2, 2] 
    },
    "polygon": {
        "path": "/data/Segmetnation_Results/cell_polygons.geojson",
        "z_plane": None,
    },
    "output_path": "/scratch/1305732956.zarr",
}

image_dir = config["input_path"] + "images"

image_config = config["image"]

print(read_merscope_stain_imagestack(image_dir, **image_config))
