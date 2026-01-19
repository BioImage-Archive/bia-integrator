# Persistence

## Mongo API persistance 

Client logic to handle pushing objects to the mongo API.

Set credentials via .env file, using .env_template as a guide. 

## S3 interaction

For uploading data to S3 storage. 

Configuration options are provided in .env_template, and should be specified in a .env file for use. Note that while `endpoint_url` has a default value in `settings.py`, there is not a valid bucket name, the idea being that we are then forced to think about where we want to put data. Generally, it is expected that the bucket name will be set in other places, such as [`bia-converter`](https://github.com/BioImage-Archive/bia-integrator/tree/main/bia-converter) or [`annotation-data-converter`](https://github.com/BioImage-Archive/bia-integrator/tree/main/annotation-data-converter), which use the S3 upload function found here.

The `aws_access_key_id` and `aws_secret_access_key` values can be set in your .env file, or specified in a configuration file, according to these [instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).