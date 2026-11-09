# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/share-folder <<'EOF'
#!/bin/bash
# Usage: share-folder GROUP DIR USER...
# A folder for a group: the group may do everything in it, others nothing,
# and each USER is added to the group (keeping their other groups).
group="$1"
dir="$2"
shift 2
getent group "$group" > /dev/null || sudo groupadd "$group"
sudo mkdir -p "$dir"
sudo chgrp "$group" "$dir"
# 2770: owner and group may do everything, others nothing, and the 2 (the
# setgid bit) makes new files inside belong to the group too.
sudo chmod 2770 "$dir"
for user in "$@"; do
  sudo usermod -aG "$group" "$user"
done
ls -ld "$dir"
EOF
chmod +x ~/bin/share-folder
~/bin/share-folder deploy /srv/app ada ben
id ada
