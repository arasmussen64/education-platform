# Wrong: assumes the group already exists, so for a new group chgrp and
# usermod both fail and the folder stays root's.
mkdir -p ~/bin
cat > ~/bin/share-folder <<'EOF'
#!/bin/bash
group="$1"
dir="$2"
shift 2
sudo mkdir -p "$dir"
sudo chgrp "$group" "$dir"
sudo chmod 2770 "$dir"
for user in "$@"; do
  sudo usermod -aG "$group" "$user"
done
EOF
chmod +x ~/bin/share-folder
