# Satellite field monitoring

The objective of this assignment is to create a daily process that uses public NASA imagery from Landsat 8 constellation to monitor a list of fields. The imagery is provided by NASA throuhg Earth API (see https://api.nasa.gov)). The service requires an API key that can be obtained for free.

## Part 1: Process implementation

Implement a process in Python that given a date and the locations of a list of fields downloads available images from NASA's Earth API. The images shall be stored in a S3 bucket with the following folder structure: `s3://{BUCKET_NAME}/{field_id}/{date}\_imagery.png`

Assume that the fields' location is stored in a csv file with the format: field_id, lat, lon, dim (width and height of field in degrees).

## Part 2: Infrastructure

Define a possible cloud arquitecture to run this process on a daily basis.

## Notes

- Use concurrency of any kind to retreive and save the images as fast as possible.
- To mock AWS S3 you can use the moto library (https://docs.getmoto.org/). It shall be easy to switch to the real S3 service.
- The process shall run within its own docker container. Configuration shall be provided as enviroment variables to the container (date, destination bucket, AWS credentials, API key, etc.)
- If possible, create a new GitHub repository with the solution.
- Document usage in a README file.
- Tests are always welcome!
