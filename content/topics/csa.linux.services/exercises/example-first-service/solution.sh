cat ~/heartbeat.service
sudo cp ~/heartbeat.service /etc/systemd/system/heartbeat.service
sudo systemctl daemon-reload
sudo systemctl enable --now heartbeat
systemctl status heartbeat --no-pager
journalctl -u heartbeat -n 3 --no-pager
