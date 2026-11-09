# Wrong: without apt update, apt knows of no packages at all: nothing to
# install, nothing waiting.
apt list --upgradable
sudo apt install -y shop-dashboard || true
mkdir -p ~/example && apt list --upgradable > ~/example/upgradable.txt
