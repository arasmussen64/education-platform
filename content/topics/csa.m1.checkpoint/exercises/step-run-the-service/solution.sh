# The one part left: enable the service so it starts on boot, and start it now.
sudo systemctl enable --now shop-api
sleep 1; curl -s localhost:8080
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
