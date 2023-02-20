# Dstl (Team 1)

Team from the Defence Science and Technology Laboratory (Dstl) in the UK.

## Solution workflow

Our proposed workflow is currently as follows:

![Proposed workflow](docs/workflow.png)

1) Convert video into frames, or start with a series of frames (e.g. 1 a second)
2) From the frames, generate a map of the environment based on looking for overlap in the images. This stage includes determining our current location, which is known from the last frame we have processed.
3) Segment the generated map into buildings, fields, roads, rivers, etc. This step will hopefully help mitigate differences between current and reference mapping, and reduce the effect of weather.
4) Register the segemented generated map to a segmented reference map (or vector reference map). This allows us to go from our known position within the generated map to a known position on the ground.

Once we know where we are, then it is a relatively straightforwards task to calculate a route back to a safe location or to retrace our previous route.

## Infrastructure

The following components are created as part of our infrastructure, which is hosted on AWS. The infrastructure is defined using Terraform to provide IaC.

* `videos` bucket - an S3 bucket containing the original raw data
* `frames` bucket - an S3 bucket containing frames extracted from each video
* `ref` bucket - an S3 bucket containing reference data, including reference mapping

## Reference Mapping

Reference mapping is extracted from OSM (OpenStreet Maps) and converted to a GeoTIFF for features of interest (as extracted by the segmentation stage). An example of extracting highway features for a 0.2 x 0.25 degree box at 0.00001 degree resolution is as follows:

```
# Filter to features
osmium tags-filter europe-latest.osm.pbf wr/highway -o highways.osm.pbf

# Flatten to GeoTIFF, ignoring points
gdal_rasterize -burn 255 highways.osm.pbf highways.gtiff -l lines -l multilinestrings -l multipolygons -f "GTiff" -te 15.0 28.45 15.2 28.7 -tr 0.00001 0.00001
```

 The features, and the associated OSM tags, are:

* Buildings (`wr/building`)
* Roads (`wr/highway`)
* Water (`wr/water`)

Anything not covered by one of those layers is assumed to be land or vegetation (the other categories of the segmentation).