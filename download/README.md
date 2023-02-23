# Download

Downloads, merges and georeferences tiles for an area around a given central point.
Based on https://github.com/jimutt/tiles-to-tiff

## Usage

You can run the script using `python3 download.py LONGITUDE LATITUDE`.

A `config.json` file is required to be in the same directory that you are running the script from (see below for format), but you can also override the values in the configuration file via the command line.

### config.json

The following provides an example `config.json` using MapTiler as the tile source.

```
{
    "bbox": {
        "width": 0.05,
        "height": 0.05
    },
    "url": "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key=KEY"
    "output": "./merged_tiles.tif",
    "zoom": 16
}
```

`KEY` should be replaced with your MapTiler API key.

If you want to download tiles from Google Maps rather than MapTiler (be careful about Google Maps T&Cs), then you can use the following URL: `http://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}`.

### Command Line Options

The following additional command line options can be provided, and will override values set in `config.json`

| Short Option | Long Option | Description |
| ------------ | ----------- | ----------- |
| -h | --height | Height of the bounding box in degrees |
| -o | --output | Output file |
| -u | --url | URL of the map tile server, with {x}, {y} and {z} variables |
| -w | --width | Width of the bounding box in degrees |
| -z | --zoom | Zoom level |
