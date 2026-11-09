# Wrong: 777 lets every account on the machine read and change the service's files.
cat > ~/bin/add-service-account <<'EOF'
#!/bin/bash
name="$1"
dir="$2"
sudo useradd --system --no-create-home --shell /usr/sbin/nologin "$name"
sudo mkdir -p "$dir"
sudo chown "$name":"$name" "$dir"
sudo chmod 777 "$dir"
EOF
