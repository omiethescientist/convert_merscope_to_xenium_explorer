from spatialdata.transformations import BaseTransformation
from spatialdata.models import ShapesModel
import geopandas as gpd
from geopandas import GeoDataFrame
from pathlib import Path
import geojson
from shapely import MultiPolygon


def get_sis_polygons(
    path: Path | str,
    transformations: BaseTransformation,
    z_plane: int | list[int] | None = None,
) -> GeoDataFrame:
    """
    Custom function for loading polygons generated from spots-in-space for appending into a SpatialData

    Parameters:
    path : {str or pathlib.Path}
        Location of geojson of sis polygons.
    transformations : {spatialdata.transformations.BaseTransformation}
        Image transformation for polygon to pixel conversion
    z_plane : {int, list of ints, or None}, optional
        z_plane or planes that we select. If none, will aggregate polygons across all z_layers.

    Returns:
    geo_df : GeoDataFrame
        geopandas dataframe of polygons to add to SpatailData object.
    """
    # load json
    with open(path) as f:
        features = geojson.load(f)

    # format the features
    format_features = [
        {
            "geometry": feature["geometry"],
            "properties": {"id": feature["id"], "z_plane": feature["z_plane"]},
        }
        for feature in features["features"]
    ]
    format_features = geojson.FeatureCollection(format_features)

    # Generate geopandas df
    geo_df = gpd.GeoDataFrame.from_features(format_features)

    # Select a layer or take the union across all layers
    if z_plane is None:
        geo_df = geo_df.dissolve(by="id")
    else:
        if type(z_plane) is not list:
            z_plane = [z_plane]
        z_plane = [str(z) for z in z_plane]
        geo_df = geo_df[geo_df["z_plane"].isin(z_plane)]
        geo_df.index = geo_df["id"].astype(str)

    # Remove empty or non-valid geometries
    geo_df = geo_df[(geo_df["geometry"].is_valid) & (~geo_df["geometry"].is_empty)]

    # Combine Multipolygons by taking their convex hull. This might make for larger areas, but this usually represents a minority of cells.
    geo_df["geometry"] = geo_df["geometry"].apply(
        lambda x: x.convex_hull if type(x) is MultiPolygon else x
    )
    return ShapesModel.parse(geo_df, transformations=transformations)
