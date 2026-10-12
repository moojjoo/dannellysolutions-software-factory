#!/usr/bin/env bash
# Read-only AWS / Docker preflight. Requires environment-specific configuration.
set -euo pipefail
: "${AWS_ACCOUNT_ID:?Expected AWS account required}"
: "${AWS_REGION:?Expected AWS region required}"
: "${REQUIRED_SECRET_IDS:?Space-separated secret ARNs required}"
: "${REQUIRED_DOCKER_VOLUMES:?Space-separated existing volume names required}"
actual="$(aws sts get-caller-identity --query Account --output text)"
[[ "$actual" == "$AWS_ACCOUNT_ID" ]] || { echo "Wrong AWS account"; exit 1; }
for secret in $REQUIRED_SECRET_IDS; do
  aws secretsmanager describe-secret --secret-id "$secret" --region "$AWS_REGION" --query ARN --output text >/dev/null
done
docker info >/dev/null
for volume in $REQUIRED_DOCKER_VOLUMES; do
  docker volume inspect "$volume" >/dev/null
done
# Deployment-specific IAM permissions, mounts, write access and SSM checks must be
# added by the consuming application; this baseline is not a deployment approval.
echo "Baseline preflight passed; application-specific checks still required"
