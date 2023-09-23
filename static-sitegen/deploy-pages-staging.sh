BUCKET_NAME=bia-pages-staging
aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 sync tmp/pages/ s3://${BUCKET_NAME}/pages --acl public-read
aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp BIA-Logo.png s3://${BUCKET_NAME}/assets/BIA-Logo.png --acl public-read
