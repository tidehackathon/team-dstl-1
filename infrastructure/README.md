# Infrastructure

The following components were created as part of our infrastructure (hosted on AWS) to help our team coordinate and share data. The infrastructure is defined using Terraform to provide IaC, and will be destroyed after the event.

* `videos` bucket - an S3 bucket containing the original raw data
* `frames` bucket - an S3 bucket containing frames extracted from each video
* `ref` bucket - an S3 bucket containing reference data, including reference mapping