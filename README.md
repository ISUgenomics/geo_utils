# geo_utils
The collection of small Python-based utilities for geospatial analysis.

---

The **geo_utils** repository houses an evolving collection of **Python utilities tailored for geospatial analysis**. These utilities are **designed to complement photogrammetry analysis using ODM software**, enhancing the robustness of processing pipelines especially **when calculations are executed on an HPC cluster**. As the repository grows, it aims to serve a broader range of geospatial needs while maintaining its core focus on delivering efficient and precise tools.

---

## Table of Contents:

[License](#license)

| tool                       | category       | description |
|----------------------------|----------------|-------------|
|[gcp_images_picker.py](#gcp-images-picker)      | [georeferencing](#georeferencing) | Automated selector for representative GCP images, minimizing manual inspection.|
|[gcp_to_aruco_mapper.py](#gcp-to-aruco-mapper)  | [georeferencing](#georeferencing) | Maps custom GCP IDs to corresponding ArUco marker IDs in imagery based on the distance between GCP coordinates and image GPS.|


## License

```
# Copyright (c) 2023 Aleksandra Badaczewska
#
# GNU GENERAL PUBLIC LICENSE, version 3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

# Photogrammetry

## Georeferencing

---

### GCP images picker

**Applications:** This script selects the most representative images for Ground Control Points (GCPs) in land surveying projects. It calculates the Euclidean distance of each marker from the center of the image, sorts them in ascending order, and picks the top N images for each marker ID.

**Usage Stage:** This utility is especially useful in the data preparation phase before running photogrammetry analysis (e.g., using ODM software). The script streamlines the image selection process by automatically (programmatically) identifying the most representative photos for each GCP, reducing the need for time-consuming visual inspections. It is especially useful when dealing with datasets that may contain thousands of images.

---

### GCP to ArUco mapper

**Applications:** This script identifies which custom GCP IDs match with ArUco marker IDs present in the images. It is intended to create a mapping between images and their corresponding GCPs, providing a reliable set of control points for georeferencing.

**Usage Stage:** This script is typically employed during the initial stages of a land surveying project, after capturing the images and prior to photogrammetry processing. The tool is crucial when you have the recorded reference GCP coordinates with custom IDs that differ from the ArUco marker IDs, and you need to establish which custom IDs correspond to which ArUco marker IDs.

```
*********************************
Maps custom GCP IDs to corresponding ArUco marker IDs in imagery (uses WGS84 datum).
*********************************

python3 gcp_to_aruco_mapper.py -h

optional arguments:
  -h,               --help                           show this help message and exit
  -g GCP_FILE,      --gcp-file GCP_FILE              Path to the GCP file
  -i IMAGERY_PATH,  --imagery-path IMAGERY_PATH      Path to the imagery directory
  -z ZONE,          --zone ZONE                      UTM Zone
  -o OUTPUT,        --output OUTPUT                  Path to the output file
  -d MAX_DIST,      --max_dist MAX_DIST              Distance threshold in meter

USAGE:
     gcp_to_aruco_mapper.py [-h] -g GCP_FILE -i IMAGERY_PATH -z ZONE [-o OUTPUT] [-d MAX_DIST]
Example:
     python gcp_to_aruco_mapper.py -g <gcp_file> -i <imagery_dir> -z 11 -o <output_file> -d 50
```


```
python3 <your_path>/geo_utils/TOOLS/gcp_to_aruco_mapper.py -g gcp_list.txt -i "./" -z 11 -o out -d 50 > err
```

---
