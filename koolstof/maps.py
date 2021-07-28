import itertools
import vptree
from geographiclib.geodesic import Geodesic
import cartopy.io.shapereader as shpreader
from shapely.geometry import LinearRing


def geodesic_distance(lon_lat_1, lon_lat_2):
    """Calculate geodesic distance between a pair of points in km.

    Based on https://stackoverflow.com/a/45480555
    """
    return (
        Geodesic.WGS84.Inverse(lon_lat_1[1], lon_lat_1[0], lon_lat_2[1], lon_lat_2[0])[
            "s12"
        ]
        / 1000
    )


def coastline_coords(lat_range, lon_range, resolution="10m"):
    """Get list of coastline coordinates from Natural Earth Data coastline sections
    that intersect with the lat_range and lon_range.
    """
    x = shpreader.natural_earth(resolution="10m", category="physical", name="coastline")
    cl = shpreader.Reader(x)
    coastlines = cl.records()
    my_bounds = LinearRing(
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

    Use vpt.get_nearest_neighbor((lon, lat)) to find geodesic distance of nearest point
    on the coastline to (lon, lat) in km.

    Based on https://stackoverflow.com/a/45480555
    """
    coords = coastline_coords(lat_range, lon_range, **kwargs)
    vpt = vptree.VPTree(coords, geodesic_distance)
    return vpt
