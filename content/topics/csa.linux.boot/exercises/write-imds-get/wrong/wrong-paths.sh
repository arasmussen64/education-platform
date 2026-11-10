# Wrong: the zone and region come from the top-level meta-data paths, which
# don't exist; placement/ is where they live. The lines come out empty.
cat > ~/bin/instance-facts <<'EOF'
#!/bin/bash
set -euo pipefail
imds=http://169.254.169.254
token=$(curl -sX PUT "$imds/latest/api/token" -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')
get() { curl -s -H "X-aws-ec2-metadata-token: $token" "$imds/latest/meta-data/$1"; }
echo "instance-id: $(get instance-id)"
echo "zone: $(get availability-zone)"
echo "region: $(get region)"
EOF
chmod +x ~/bin/instance-facts
