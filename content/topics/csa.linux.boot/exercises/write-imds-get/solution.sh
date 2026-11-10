# The reference client, written in one go; in the lab you'd use nano.
cat > ~/bin/instance-facts <<'EOF'
#!/bin/bash
# Usage: instance-facts
# Who this instance is, asked of the metadata service the session-based way:
# a token first, then that token on every request.
set -euo pipefail
imds=http://169.254.169.254
token=$(curl -sX PUT "$imds/latest/api/token" -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')

get() {
  curl -s -H "X-aws-ec2-metadata-token: $token" "$imds/latest/meta-data/$1"
}

echo "instance-id: $(get instance-id)"
echo "zone: $(get placement/availability-zone)"
echo "region: $(get placement/region)"
EOF
chmod +x ~/bin/instance-facts
~/bin/instance-facts
echo "--- now require tokens and run it again"
lab-imds-options --tokens required
~/bin/instance-facts
