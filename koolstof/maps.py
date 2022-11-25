import itertools
import vptree
from geographiclib.geodesic import Geodesic
import cartopy.io.shapereader as shpreader
from shapely import geometry


def geodesic_distance(lon_lat_1, lon_lat_2):
    """Calculate geodesic distance between a single pair of points in km, based on
    https://stackoverflow.com/a/45480555

    Parameters
    ----------
    lon_lat_1 : array_like
        (longitude, latitude) of the first point in decimal degrees.
    lon_lat_2 : array_like
        (longitude, latitude) of the second point in decimal degrees.

    Returns
    -------
    float
        Distance between the two points in km.
    """
    return (
        Geodesic.WGS84.Inverse(lon_lat_1[1], lon_lat_1[0], lon_lat_2[1], lon_lat_2[0])[
            "s12"
        ]
        / 1000
    )


def _coastline_coords(lat_range, lon_range, resolution="10m"):
    """Get list of coastline coordinates from Natural Earth Data coastline sections
    that intersect with the lat_range and lon_range.

    Parameters
    ----------
    lat_range : array_like
        (min, max) latitude in decimal degrees.
    lon_range : array_like
        (min, max) longitude in decimal degrees.
    resolution : str, optional
        Natural Earth Data resolution, by default "10m"

    Returns
    -------
    list
        Coordinates of the matching coastlines.
    """
    assert resolution in ["10m", "50m", "110m"]
    x = shpreader.natural_earth(
        resolution=resolution, category="physical", name="coastline"
    )
    cl = shpreader.Reader(x)
    coastlines = cl.records()
    my_bounds = geometry.Polygon(
        [
            (lon_range[0], lat_range[0]),
            (lon_range[0], lat_range[1]),
            (lon_range[1], lat_range[1]),
            (lon_range[1], lat_range[0]),
        ]
    )
    in_bounds = [cl for cl in coastlines if cl.geometry.intersects(my_bounds)]
    coords = list(itertools.chain(*[ib.geometry.coords for ib in in_bounds]))
    return coords


def build_vptree(lat_range, lon_range, **kwargs):
    """Build vantage-point tree from Natural Earth Data coastline sections that
    intersect with the lat_range and lon_range.

    Once constructed, use `vpt.get_nearest_neighbor((lon, lat))` to find the geodesic
    distance of nearest point on the coastline to (lon, lat) in km.

    Based on https://stackoverflow.com/a/45480555

    Parameters
    ----------
    lat_range : array_like
        (min, max) latitude in decimal degrees.
    lon_range : array_like
        (min, max) longitude in decimal degrees.

    Returns
    -------
    vpt : vptree.VPTree
        Vantage-point tree containing the matching coastline sections.
    """
    coords = _coastline_coords(lat_range, lon_range, **kwargs)
    vpt = vptree.VPTree(coords, geodesic_distance)
    return vpt
