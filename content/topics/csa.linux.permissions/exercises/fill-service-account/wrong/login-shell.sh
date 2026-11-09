# Wrong: /bin/bash as the shell means someone who gets the account's
# password, or a key into it, gets a working login.
cat > ~/bin/add-service-account <<'EOF'
#!/bin/bash
name="$1"
dir="$2"
sudo useradd --system --no-create-home --shell /bin/bash "$name"
sudo mkdir -p "$dir"
sudo chown "$name":"$name" "$dir"
sudo chmod 750 "$dir"
EOF
