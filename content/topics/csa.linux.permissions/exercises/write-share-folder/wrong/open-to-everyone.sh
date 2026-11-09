# Wrong: 777 means the group was pointless; everyone can do everything.
mkdir -p ~/bin
cat > ~/bin/share-folder <<'EOF'
#!/bin/bash
group="$1"
dir="$2"
shift 2
getent group "$group" > /dev/null || sudo groupadd "$group"
sudo mkdir -p "$dir"
sudo chgrp "$group" "$dir"
sudo chmod 777 "$dir"
for user in "$@"; do
  sudo usermod -aG "$group" "$user"
done
EOF
chmod +x ~/bin/share-folder
