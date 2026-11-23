#!/bin/bash
# Builds the lab's scenery while the image is built: the recipe and the
# build script with their gaps (copied in by the Dockerfile) made the
# learner's, the image's one own file, and the package server's folder.
# The package token is made at the machine's first boot (bao-seed.sh).
set -euo pipefail

install -d -o learner -g learner /home/learner/bin /home/learner/shop-export
install -o learner -g learner -m 755 /tmp/build-shop /home/learner/bin/build-shop
install -o learner -g learner -m 644 /tmp/Containerfile /home/learner/shop-export/Containerfile

cat > /home/learner/shop-export/app.sh << 'EOF'
#!/bin/sh
# The export job, as far as this lab goes: it says which library it has.
echo "shop-export, with $(cat /opt/shop-lib.txt)"
EOF
chown learner:learner /home/learner/shop-export/app.sh

# The package server's state: its token and the library it serves. Only
# root reads the folder.
install -d -m 700 /var/lib/pkg-server
echo "shop-lib 2.4.1" > /var/lib/pkg-server/library
