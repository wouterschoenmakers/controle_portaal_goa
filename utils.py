import numpy as np
import geopandas as gpd
import pandas as pd

def buffer(row):
    try:
        return row.buffer(0)
    except:
        return None

def add_metrics(result):
    result = result.rename(columns={"geometry": "geometry_left"})
    result["geometry_left"] = result.set_geometry("geometry_left").apply(lambda x: buffer(x["geometry_left"]), axis=1)
    result["geometry_right"] = result.set_geometry("geometry_right").apply(lambda x: buffer(x["geometry_right"]),
                                                                           axis=1)
    result["overlap_geometry"] = gpd.GeoSeries(result.geometry_left).intersection(gpd.GeoSeries(result.geometry_right))
    result["overlap_area"] = result.set_geometry("overlap_geometry").area
    result["overlap_percentage"] = (np.min(
        [result.overlap_area, result.set_geometry("geometry_left").area, result.set_geometry("geometry_right").area],
        axis=0) / np.min([result.set_geometry("geometry_left").area, result.set_geometry("geometry_right").area],
                         axis=0)) * 100
    result["oppervlak_percentage"] = (np.min(
        [result.set_geometry("geometry_left").area, result.set_geometry("geometry_right").area], axis=0) / np.max(
        [result.set_geometry("geometry_left").area, result.set_geometry("geometry_right").area], axis=0)) * 100
    return result


def process_geometries(left_df: gpd.GeoDataFrame, right_df: gpd.GeoDataFrame, how: str) -> gpd.GeoDataFrame:
    left_df = left_df.reset_index(drop=True)
    right_df = right_df.reset_index(drop=True)
    result = add_metrics(
        left_df.reset_index(drop=True).sjoin(right_df, how=how, predicate="intersects")
        .assign(
            geometry_right=lambda df: [right_df.geometry.iloc[ind] for ind in df.index_right if isinstance(ind, int)])
    )

    return result