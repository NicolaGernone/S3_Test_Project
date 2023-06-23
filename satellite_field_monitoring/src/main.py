from services.satellite import S3Services
from services.ndvi import NDVIServices

def main():
    # Initialize a FieldMonitor and NVDIinputs instance
    field_monitor = S3Services.FieldMonitor()
    paths = NDVIServices.NDVIInputs()

    # Start monitoring fields
    S3Services.monitor_fields(field_monitor)
    
    #Calculate NDVI and generate report
    NDVIServices.ndvi_report(paths)

if __name__ == "__main__":
    main()
