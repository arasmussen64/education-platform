# The finished script. In the lab you'd fill the three gaps with nano; here
# it's written in one go.
cat > ~/bin/add-service-account <<'EOF'
#!/bin/bash
# Usage: add-service-account NAME DIR
# Makes a service account called NAME: a system user that nobody can log in
# as, with a group of its own, owning DIR, which only it and its group may
# enter.
name="$1"
dir="$2"
sudo useradd --system --no-create-home --shell /usr/sbin/nologin "$name"
sudo mkdir -p "$dir"
sudo chown "$name":"$name" "$dir"
sudo chmod 750 "$dir"
echo "$name now owns $dir:"
ls -ld "$dir"
EOF
~/bin/add-service-account reports /srv/reports
getent passwd reports
