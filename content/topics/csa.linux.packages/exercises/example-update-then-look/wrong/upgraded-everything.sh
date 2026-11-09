# Wrong: upgraded everything before looking, so the saved list is empty and
# the untested report tool changed under the team.
sudo apt update
sudo apt upgrade -y
sudo apt install -y shop-dashboard
mkdir -p ~/example && apt list --upgradable > ~/example/upgradable.txt
