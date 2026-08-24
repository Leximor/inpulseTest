#!/bin/sh
set -e

# Substitute DOMAIN at container start. Image rebuild is not required.
# envsubst '${DOMAIN}' keeps nginx vars ($host, $scheme, $request_uri).
envsubst '${DOMAIN}' \
    < /etc/nginx/nginx.conf.template \
    > /etc/nginx/nginx.conf

nginx -t
