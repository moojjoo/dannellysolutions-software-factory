#!/usr/bin/env bash
# Read-only drift check. No apply. Requires configured Terraform backend.
set -euo pipefail
terraform init -input=false -lockfile=readonly
set +e
terraform plan -refresh-only -detailed-exitcode -input=false -lock=true -out=tfdrift.plan >/dev/null
status=$?
set -e
rm -f tfdrift.plan
case "$status" in
  0) echo "No Terraform drift"; exit 0 ;;
  2) echo "Terraform drift detected; manual investigation required"; exit 2 ;;
  *) echo "Terraform drift check failed"; exit 1 ;;
esac
