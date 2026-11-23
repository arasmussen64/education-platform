# Wrong: the token is made an environment variable of the image, which
# every container started from it gets, and which the image's settings
# show to anyone.
cat > ~/shop-export/Containerfile << 'EOF'
FROM busybox
ARG PKG_TOKEN
ENV PKG_TOKEN=$PKG_TOKEN
RUN wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $PKG_TOKEN" http://127.0.0.1:8081/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
cat > ~/bin/build-shop << 'EOF'
#!/bin/bash
set -euo pipefail
sudo podman build -q --build-arg PKG_TOKEN="$(bao kv get -field=token secret/ci/pkg-token)" -t shop-export:2 ~/shop-export
EOF
