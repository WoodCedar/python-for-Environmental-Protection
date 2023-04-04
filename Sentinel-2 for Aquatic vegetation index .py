'''
date:20230404
Email:zhb1227@126.com
purpose:Calculation of EVSI, SVSI, MNDWI and TC using Sentinel 2 satellite
environment:python 3.9
'''
import rasterio
import numpy as np
import os
from rasterio.transform import Affine

sentinel_image_filepath = 'F:\\duty\\2022年\\th20220811cutrs.tif'
sentinel_date = 'TH202208011'
output_folder = "E:\\th\index"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read Sentinel-2 image
with rasterio.open(sentinel_image_filepath) as src:
    green_band = src.read(3)
    red_band = src.read(4)
    nir_band = src.read(8)
    swir_band = src.read(11)
    profile = src.profile


# Calculate MNDWI
epsilon = 1e-8
mndwi = (green_band.astype(float) - swir_band.astype(float)) / (green_band.astype(float) + swir_band.astype(float) + epsilon)

# Calculate EVSI
evsi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band.astype(float) + red_band.astype(float) + epsilon)

# Tasseled Cap Transformation coefficients for Sentinel-2
tct_coeffs = np.array([
    [0.3037, 0.2793, 0.4743, 0.5585],
    [-0.2848, -0.2435, -0.5436, 0.7531],
    [0.1509, 0.1973, 0.3279, 0.3406]
])

# Stack bands for TCT calculation
stacked_bands = np.array([green_band, red_band, nir_band, swir_band])

# Calculate Tasseled Cap Transformation
tct = np.zeros((3, green_band.shape[0], green_band.shape[1]))
for i in range(3):
    for j in range(4):
        tct[i] += tct_coeffs[i, j] * stacked_bands[j]

# Calculate SVSI
svsi = tct[0] - tct[1]  # TC1 - TC2

# Save the calculated indices as GeoTIFF files
sentinel_date = 'TH202208011'  # Replace this with the actual date from the Sentinel-2 image

output_filename_mndwi = f"{output_folder}{sentinel_date}_MNDWI.tif"
output_filename_evsi = f"{output_folder}{sentinel_date}_EVSI.tif"
output_filename_tct = f"{output_folder}{sentinel_date}_"
output_filename_svsi = f"{output_folder}{sentinel_date}_SVSI.tif"

index_profile = profile.copy()
index_profile.update(dtype=rasterio.float32, count=1)

with rasterio.open(output_filename_mndwi, 'w', **index_profile) as dst:
    dst.write(mndwi.astype(rasterio.float32), 1)

with rasterio.open(output_filename_evsi, 'w', **index_profile) as dst:
    dst.write(evsi.astype(rasterio.float32), 1)
with rasterio.open(output_filename_svsi, 'w', **index_profile) as dst:
    dst.write(svsi.astype(rasterio.float32), 1)
for i, name in enumerate(['Brightness', 'Greenness', 'Wetness']):
    with rasterio.open(f"{output_filename_tct}{name}.tif", 'w', **profile) as dst:
        dst.write(tct[i].astype(rasterio.float32), 1)

print(f"Generated files: {output_filename_mndwi}, {output_filename_evsi}, {output_filename_tct}Brightness.tif, {output_filename_tct}Greenness.tif, {output_filename_tct}Wetness.tif, {output_filename_svsi}")
