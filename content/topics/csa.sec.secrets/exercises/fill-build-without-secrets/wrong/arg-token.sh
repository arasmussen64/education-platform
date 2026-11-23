# Wrong: last year's way. The token is handed to the build as a build
# argument, which the image's history keeps for every later step.
cat > ~/shop-export/Containerfile << 'EOF'
FROM busybox
ARG PKG_TOKEN
RUN wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $PKG_TOKEN" http://127.0.0.1:8081/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
cat > ~/bin/build-shop << 'EOF'
#!/bin/bash
set -euo pipefail
sudo podman build -q --build-arg PKG_TOKEN="$(bao kv get -field=token secret/ci/pkg-token)" -t shop-export:2 ~/shop-export
EOF
