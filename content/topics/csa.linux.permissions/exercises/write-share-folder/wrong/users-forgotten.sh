# Wrong: the folder is set up but nobody is added to the group.
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
EOF
chmod +x ~/bin/share-folder
