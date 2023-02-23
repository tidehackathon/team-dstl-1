import urllib.request
import os
from tile_convert import bbox_to_xyz, tile_edges
from osgeo import gdal

cache_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'cache'))

def fetch_tile(x, y, z, tile_source):
    url = tile_source.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))

    if not tile_source.startswith("http"):
        return url.replace("file:///", "")

    path = f'{cache_dir}/{x}_{y}_{z}.png'

    if not os.path.exists(path):
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) tiles-to-tiff/1.0 (+https://github.com/jimutt/tiles-to-tiff)'
            }
        )
        g = urllib.request.urlopen(req)
        with open(path, 'b+w') as f:
            f.write(g.read())
        
        print(f"{x},{y} fetched")

    
    return path


def merge_tiles(tiles, output_path):
    vrt_path = cache_dir + "/tiles.vrt"
    gdal.BuildVRT(vrt_path, tiles)
    gdal.Translate(output_path, vrt_path)


def georeference_raster_tile(x, y, z, path):
    tile = os.path.join(cache_dir, f'{cache_dir}/{x}_{y}_{z}.tif')

    if not os.path.exists(tile):
        bounds = tile_edges(x, y, z)
        gdal.Translate(tile,
                    path,
                    outputSRS='EPSG:4326',
                    outputBounds=bounds)
    
    return tile

def convert(tile_source, output_file, bounding_box, zoom): 
    lon_min, lat_min, lon_max, lat_max = bounding_box

    # Script start:
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    x_min, x_max, y_min, y_max = bbox_to_xyz(
        lon_min, lon_max, lat_min, lat_max, zoom)

    print(f"Fetching & georeferencing {(x_max - x_min + 1) * (y_max - y_min + 1)} tiles")

    tiles = []
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            try:
                png_path = fetch_tile(x, y, zoom, tile_source)
                tile = georeference_raster_tile(x, y, zoom, png_path)

                tiles.append(tile)
            except OSError as e:
                print(f"Error ({str(e)}), failed to get {x},{y}")
                pass

    print("Resolving and georeferencing of raster tiles complete")

    print("Merging tiles")
    merge_tiles(tiles, output_file)
    print("Merge complete")
