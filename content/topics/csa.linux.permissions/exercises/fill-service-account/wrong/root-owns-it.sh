# Wrong: the folder stays root's, so the service can't write to its own folder.
cat > ~/bin/add-service-account <<'EOF'
#!/bin/bash
name="$1"
dir="$2"
sudo useradd --system --no-create-home --shell /usr/sbin/nologin "$name"
sudo mkdir -p "$dir"
sudo chown root:"$name" "$dir"
sudo chmod 750 "$dir"
EOF
