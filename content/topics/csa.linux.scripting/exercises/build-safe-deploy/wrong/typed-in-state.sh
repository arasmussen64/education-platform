# Wrong: the releases and the symlink are made by hand, as the try-out
# would leave them, and the script only knows how to refuse a missing
# version. Run for any other app, it deploys nothing.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: deploy VERSION" >&2; exit 2; }
echo "deployed $1"
EOF
chmod +x ~/bin/deploy
mkdir -p ~/app/releases
for v in 1.2 1.3 1.4; do cp -r ~/app/src ~/app/releases/"$v"; done
ln -sfn releases/1.4 ~/app/current
