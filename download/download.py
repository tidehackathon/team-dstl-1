import argparse
import json

from tiles_to_tiff import convert

if __name__=="__main__":

    with open("config.json") as f:
        config = json.load(f)
    
    a = argparse.ArgumentParser(
        prog = 'Download Mapping',
        description = 'Downloads map tiles around a point and merges them into a single georeferenced TIFF',
        add_help=False
    )

    a.add_argument("longitude", help="Longitude", type=float)
    a.add_argument("latitude", help="Latitude", type=float)

    a.add_argument("--width", "-w", help="Width of the bounding box, in degrees", type=float, default=config['bbox']['width'])
    a.add_argument("--height", "-h", help="Height of the bounding box, in degrees", type=float, default=config['bbox']['height'])
    a.add_argument("--output", "-o", help="Output folder", default=config['output'])
    a.add_argument("--url", "-u", help="URL of the map tile server, with {x}, {y} and {z} variables", default=config['url'])
    a.add_argument("--zoom", "-z", help="Zoom level", type=int, default=config['zoom'])

    a.add_argument('--help', action='help')

    args = a.parse_args()

    bounds = [
        args.longitude - (args.width / 2),
        args.latitude - (args.height / 2),
        args.longitude + (args.width / 2),
        args.latitude + (args.height / 2)
    ]

    convert(args.url, args.output, bounds, args.zoom)