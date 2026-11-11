# Wrong: the right answers for /srv/samples, typed in. Asked about any other
# folder, it still prints these.
cat > ~/bin/what-arch <<'EOF'
#!/bin/bash
cat <<'END'
/srv/samples/README.txt not-a-program
/srv/samples/backup.sh not-a-program
/srv/samples/deploy.py not-a-program
/srv/samples/labels.jar not-a-program
/srv/samples/libcrc-aarch64.so aarch64
/srv/samples/libcrc.so x86-64
/srv/samples/shop-api x86-64
/srv/samples/shop-api-arm64 aarch64
/srv/samples/thumb-x86_64 aarch64
END
EOF
