# Wrong: the client asks for a token but then still reads the region with a
# plain GET that doesn't carry it, so it's refused once tokens are required.
lab-imds-options --tokens required
sudo tee /usr/local/bin/region-tag > /dev/null <<'EOF'
#!/bin/bash
set -euo pipefail
imds=http://169.254.169.254
token=$(curl -sX PUT "$imds/latest/api/token" -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')
region=$(curl -s "$imds/latest/meta-data/placement/region")
echo "region: $region"
EOF
sudo chmod 755 /usr/local/bin/region-tag
