sudo apt update
apt list --upgradable
apt policy shop-agent
sudo apt install -y shop-dashboard
dpkg -l | grep shop
mkdir -p ~/example && apt list --upgradable > ~/example/upgradable.txt && cat ~/example/upgradable.txt
