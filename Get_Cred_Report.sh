#!/bin/sh

aws iam generate-credential-report
aws iam get-credential-report --output text --query Content  | base64 -D