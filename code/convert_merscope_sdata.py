from .read_spatialdata import read_merscope_sdata

# TODO: Explicitly write out configuration and test read_sdata function
# TODO: Combine configs and dump into yaml file

config = {
    "input_path": "/data/1305732956/region_0/",
    "image": {
        "stain": "DAPI",
        "z": None,
        "agg_z": "max",
        "chunk_size"": (1, 4096, 4096),
        "scale_factors": (2, 2, 2, 2)
        "image_models_kwargs": {
            "scale_factors": [2, 2, 2, 2],
            "chunks": (1, 4096, 4096),
        },
    },
    "polygon": {
        "path": "/data/Segmetnation_Results/cell_polygons.geojson",
        "z_plane": None,
    },
    "output_path": "/scratch/1305732956.zarr",
}


def main():
    sdata = read_merscope_sdata(config["input_path"], config["image"], config["polygon"])

    print("Writing spatial data")

    sdata.write(config["output_path"], overwrite=True)


if __name__ == "__main__":
    output_dir = Path(config["output_path"])
    if output_dir.exists():
        print("Zarr already created")
    else:
        main()
