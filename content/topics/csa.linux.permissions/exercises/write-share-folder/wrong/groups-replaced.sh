# Wrong: usermod -G without -a REPLACES the user's groups, so ada drops out
# of developers.
mkdir -p ~/bin
cat > ~/bin/share-folder <<'EOF'
#!/bin/bash
group="$1"
dir="$2"
shift 2
getent group "$group" > /dev/null || sudo groupadd "$group"
sudo mkdir -p "$dir"
sudo chgrp "$group" "$dir"
sudo chmod 2770 "$dir"
for user in "$@"; do
  sudo usermod -G "$group" "$user"
done
EOF
chmod +x ~/bin/share-folder
