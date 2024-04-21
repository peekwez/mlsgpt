#!/bin/bash
sudo certbot certonly \
    --manual \
    --preferred-challenges=dns \
    --email tech@kwap-consulting.com \
    --server https://acme-v02.api.letsencrypt.org/directory \
    --agree-tos \
    -d *.docex.io