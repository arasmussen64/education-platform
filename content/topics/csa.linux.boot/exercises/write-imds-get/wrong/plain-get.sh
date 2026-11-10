# Wrong: the facts are read with plain GETs and no token. It works while the
# service still allows plain requests, but breaks the moment tokens are
# required, which is exactly what the lab is about.
cat > ~/bin/instance-facts <<'EOF'
#!/bin/bash
set -euo pipefail
imds=http://169.254.169.254
echo "instance-id: $(curl -s $imds/latest/meta-data/instance-id)"
echo "zone: $(curl -s $imds/latest/meta-data/placement/availability-zone)"
echo "region: $(curl -s $imds/latest/meta-data/placement/region)"
EOF
chmod +x ~/bin/instance-facts
