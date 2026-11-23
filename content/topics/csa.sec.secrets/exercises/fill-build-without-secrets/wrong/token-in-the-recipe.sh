# Wrong: the token of the moment is typed into the recipe itself. It is
# in the history, in the file, in the repository the file is kept in,
# and the build breaks at the next rotation.
token=$(bao kv get -field=token secret/ci/pkg-token)
cat > ~/shop-export/Containerfile << EOF
FROM busybox
RUN wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $token" http://127.0.0.1:8081/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
cat > ~/bin/build-shop << 'EOF'
#!/bin/bash
set -euo pipefail
sudo podman build -q -t shop-export:2 ~/shop-export
EOF
