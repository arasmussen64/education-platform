# Wrong: the token is copied into the image as a file, used, and deleted
# by a later step. The layer that the COPY made still holds it.
cat > ~/shop-export/Containerfile << 'EOF'
FROM busybox
COPY pkg.token /tmp/pkg.token
RUN wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $(cat /tmp/pkg.token)" http://127.0.0.1:8081/shop-lib.txt
RUN rm /tmp/pkg.token
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
cat > ~/bin/build-shop << 'EOF'
#!/bin/bash
set -euo pipefail
trap 'rm -f ~/shop-export/pkg.token' EXIT
bao kv get -field=token secret/ci/pkg-token > ~/shop-export/pkg.token
sudo podman build -q -t shop-export:2 ~/shop-export
EOF
