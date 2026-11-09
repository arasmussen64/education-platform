# Wrong: the names typed in by hand, so the second account gets the first one's folder.
cat > ~/bin/add-service-account <<'EOF'
#!/bin/bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin reports
sudo mkdir -p /srv/reports
sudo chown reports:reports /srv/reports
sudo chmod 750 /srv/reports
EOF
