# Wrong: a new rule lets Ben restart the API, but the group's rule still
# names a service that doesn't exist, so Ana, the other deployer, still
# can't.
chmod 600 ~/keys/ben
sudo chmod 700 /home/ben/.ssh
echo 'ben ALL=(root) NOPASSWD: /usr/bin/systemctl restart shop-api' | sudo tee /etc/sudoers.d/ben > /dev/null
sudo chmod 440 /etc/sudoers.d/ben
sudo visudo -c
