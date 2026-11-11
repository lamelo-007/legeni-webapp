#!/bin/sh
# Usage : smoke-test.sh <projet compose> <version attendue>
set -eu
PROJECT=$1
VERSION=$2
NET=${PROJECT}_default

curl_net() { docker run --rm --network "$NET" curlimages/curl:8.11.1 "$@"; }

curl_net -sf --retry 10 --retry-connrefused --retry-delay 1 http://web:5000/ready
curl_net -sf http://web:5000/api/info | grep -Eq "\"version\": ?\"$VERSION\""
echo "Smoke test OK : $PROJECT en version $VERSION"
