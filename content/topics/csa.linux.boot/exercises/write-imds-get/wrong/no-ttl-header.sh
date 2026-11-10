# Wrong: the token request leaves out the TTL header, so the metadata
# service answers the PUT with a 400 and no token; every GET then goes out
# with an empty token and is refused once tokens are required.
cat > ~/bin/instance-facts <<'EOF'
#!/bin/bash
set -euo pipefail
imds=http://169.254.169.254
token=$(curl -sX PUT "$imds/latest/api/token")
get() { curl -s -H "X-aws-ec2-metadata-token: $token" "$imds/latest/meta-data/$1"; }
echo "instance-id: $(get instance-id)"
echo "zone: $(get placement/availability-zone)"
echo "region: $(get placement/region)"
EOF
chmod +x ~/bin/instance-facts
