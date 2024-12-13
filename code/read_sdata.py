from spatialdata import SpatialData
from spatialdata_io.readers.merscope import _rioxarray_load_merscope, _get_points
from spatialdata_io._constants._constants import MerscopeKeys
from spatialdata.transformations import Affine, BaseTransformation, Identity
from spatialdata.models import ShapesModel

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import geojson
from typing import Union
import argparse

def get_sis_polygons(path:Union[Path, str],
                     transformations:BaseTransformation,
                     z_plane:int = None):
    #load json
    with open(path) as f:
        features = geojson.load(f)

    #format the features
    format_features = [{"geometry":feature["geometry"], "properties":{"id":feature["id"], "z_plane":feature["z_plane"]}} for feature in features['features']]
    format_features = geojson.FeatureCollection(format_features)
    
    #Generate geopandas df
    geo_df = gpd.GeoDataFrame.from_features(format_features)
    
    #Select a layer or take the union across all layers
    if z_plane is None:
        geo_df = geo_df.dissolve(by = 'id')
    else:
        geo_df = geo_df[geo_df['z_plane'] == str(float(z_plane))]
        geo_df.index = geo_df['id'].astype(str)
    return ShapesModel.parse(geo_df[geo_df.is_valid], transformations = transformations)

def main():

    # Generate Image
    images_dir = input_path / 'images'

    print('... loading dapi file')
    dapi_image = _rioxarray_load_merscope(
        images_dir,
        ["DAPI"],
        3,
        {"scale_factors":[2,2,2,2], "chunks":[1, 4096, 4096]},
    )
    #
    #Get transformation matrix 
    microns_to_pixels = Affine(
        np.genfromtxt(images_dir / MerscopeKeys.TRANSFORMATION_FILE), input_axes=("x", "y"), output_axes=("x", "y")
    )

    transformations = {"global": microns_to_pixels}
    #
    ## Get points 
    print('... loading transcripts')
    transcript_path =  input_path / MerscopeKeys.TRANSCRIPTS_FILE
    points_df = _get_points(transcript_path, transformations = transformations)
    #gene_list = ['PITX2', 'CTLA4', 'NEUROD6', 'SIM1', 'LMX1A', 'TMEM200A', 'SLC17A6', 'ONECUT1', 'MS4A1', 'NPAS1', 'FOXP3', 'PAX8', 'RAB37', 'CD3D', 'SLC17A7', 'SLC17A6', 'SIM1', 'MS4A1']
    points_df = points_df.dropna()

    ##my_points = {'genes_transcripts': points_df[points_df['gene'].isin(gene_list)]}
    my_points = {'transcripts':points_df}


    #Get polygons
    print('... loading cell boundaries')
    polygons = get_sis_polygons('/data/Segmetnation_Results/cell_polygons.geojson', transformations)

    # Generate SpatialData Object
    print('... generating spatialdata object')
    my_images = {'DAPI':dapi_image}
    my_shapes = {'sis_seg':polygons}

    sdata = SpatialData(images = my_images, points = my_points, shapes = my_shapes)

    print('Writing spatial data')
    sdata.write(output_dir, overwrite = True)

if __name__ == "__main__":
    barcode = '1305732956'
    output_dir = Path(f'/scratch/{barcode}.zarr')
    input_path = Path(f'/data/1305732956/region_0/')
    if  output_dir.exists():
        print('Zarr already created')
    else:
        main()