# Wrong: the client was updated to use a token, but tokens were never
# required, so plain GETs still work and the hole is still open.
sudo tee /usr/local/bin/region-tag > /dev/null <<'EOF'
#!/bin/bash
set -euo pipefail
imds=http://169.254.169.254
token=$(curl -sX PUT "$imds/latest/api/token" -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')
region=$(curl -s -H "X-aws-ec2-metadata-token: $token" "$imds/latest/meta-data/placement/region")
echo "region: $region"
EOF
sudo chmod 755 /usr/local/bin/region-tag
