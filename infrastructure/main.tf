resource "aws_s3_bucket" "videos" {
  bucket = "${var.prefix}-videos"
}

resource "aws_s3_bucket" "frames" {
  bucket = "${var.prefix}-frames"
}