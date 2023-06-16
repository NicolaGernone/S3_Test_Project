import logging
from dataclasses import dataclass, field
from decimal import Decimal

import gdal
from decouple import config

from services.satellite import S3Services

logging.basicConfig(level=logging.DEBUG)

class NDVIServices:
    
    @dataclass
    class NDVIInputs:
        image_path: str = field(default_factory=lambda: config('IMAGE_PATH'))
        output_file: str = field(default_factory=lambda: config('REPORT_PATH'))

    @staticmethod
    def calculate_ndvi(image_path) -> Decimal:
        # Check if the image_path is an S3 URL
        if image_path.startswith('s3://'):
            image_path = S3Services.download_from_s3(image_path)

        # Open the image file
        image = gdal.Open(image_path)

        # Read the red and NIR bands
        red = image.GetRasterBand(1).ReadAsArray().astype(float)
        nir = image.GetRasterBand(2).ReadAsArray().astype(float)

        # Calculate NDVI
        ndvi = Decimal((nir - red) / (nir + red))

        return ndvi
    
    @staticmethod
    def interpret_ndvi(ndvi_value: Decimal) -> str:
        if ndvi_value < 0.1:
            return "No vegetation is present. This could be due to recently harvested crop or a fallow period."
        elif 0.1 <= ndvi_value < 0.2:
            return "Sparse vegetation is present. This might be a field in the early stage of crop growth."
        elif 0.2 <= ndvi_value < 0.4:
            return "Moderate vegetation is present. The crops are growing."
        elif 0.4 <= ndvi_value < 0.6:
            return "High vegetation is present. The crops are growing well."
        elif ndvi_value >= 0.6:
            return "Very high vegetation is present. There might be other objects (like trees) in the field."

    @staticmethod
    def ndvi_report(paths: NDVIInputs) -> None:
        # Calculate the NDVI
        ndvi_value = NDVIServices.calculate_ndvi(paths.image_path)

        # Interpret the NDVI
        interpretation = NDVIServices.interpret_ndvi(ndvi_value)

        # Log the NDVI value and its interpretation
        logging.debug(f"NDVI value: {ndvi_value}")
        logging.debug(f"NDVI interpretation: {interpretation}")

        # Write the NDVI value and its interpretation to a text file
        with open(paths.output_file, 'w') as f:
            f.write(f"NDVI value: {ndvi_value}\n")
            f.write(f"NDVI interpretation: {interpretation}\n")

