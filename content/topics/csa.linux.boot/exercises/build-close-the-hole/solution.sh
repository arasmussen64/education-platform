# 1. Require session tokens on the metadata service.
lab-imds-options --tokens required
# 2. Rewrite the shop's client to get a token and send it, so it keeps
#    working now that plain requests are refused.
sudo tee /usr/local/bin/region-tag > /dev/null <<'EOF'
#!/bin/bash
# region-tag: prints the instance's region, read from the metadata service
# with a session token (IMDSv2).
set -euo pipefail
imds=http://169.254.169.254
token=$(curl -sX PUT "$imds/latest/api/token" -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')
region=$(curl -s -H "X-aws-ec2-metadata-token: $token" "$imds/latest/meta-data/placement/region")
echo "region: $region"
EOF
sudo chmod 755 /usr/local/bin/region-tag
echo "--- a plain GET is now refused:"
curl -s -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/instance-id
echo "--- the client still works:"
region-tag
