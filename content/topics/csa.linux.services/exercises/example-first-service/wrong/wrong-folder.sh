# Wrong: /usr/lib/systemd/system belongs to packages; your units go in /etc.
sudo cp ~/heartbeat.service /usr/lib/systemd/system/heartbeat.service
sudo systemctl daemon-reload
sudo systemctl enable --now heartbeat
