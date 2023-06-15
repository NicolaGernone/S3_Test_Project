from src.services.satellite import S3Services

def main():
    # Initialize a FieldMonitor instance
    field_monitor = S3Services.FieldMonitor()

    # Start monitoring fields
    S3Services.monitor_fields(field_monitor)

if __name__ == "__main__":
    main()
