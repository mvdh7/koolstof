# Mapping tools: `ks.maps`

## Find the distance to shore

To calculate the distance between a point in space and the nearest shoreline, we can construct a vantage-point tree (VPT) from shoreline coordinates and then query it to find the closest point in space.

Constructing the VPT can take a while so we can select define ranges of latitude and longitude values and only sections of coastline that intersect these ranges are included in the analysis.  The shoreline data are downloaded automatically from [Natural Earth Data](https://www.naturalearthdata.com).  Once a VPT has been constructed it can be `pickle`d for faster future use.

### Construct the VPT

```python
import koolstof as ks

lat_range = (50, 60)
lon_range = (0, 10)
vpt = ks.maps.build_vptree(lat_range, lon_range, resolution="10m")
```

The `resolution` controls which scale of shoreline data is used: it can be `"10m"` (most detailed), `"50m"` or `"110m"`.

### Use the VPT

The VPT can only be used to compute the distance for one point at a time.

```python
lon = 55
lat = 5
distance, nearest_lon_lat = vpt.get_nearest_neighbor((lon, lat))
```

`distance` contains the distance in km to the closest point on the shoreline to `(lon, lat)`.  The coordinates of the closest point itself are given in `nearest_lon_lat`.
