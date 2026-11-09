# Wrong: everything but the secret, which everyone can still read.
sudo groupadd deploy
sudo usermod -aG deploy ada
sudo usermod -aG deploy ben
sudo chown shop:deploy /srv/shop/deploy.sh
sudo chmod 750 /srv/shop/deploy.sh
echo '%deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart shop-api' | sudo tee /etc/sudoers.d/deploy > /dev/null
sudo chmod 440 /etc/sudoers.d/deploy
sudo mkdir -p /home/ben/.ssh
sudo cp /srv/keys/ben.pub /home/ben/.ssh/authorized_keys
sudo chmod 700 /home/ben/.ssh
sudo chmod 600 /home/ben/.ssh/authorized_keys
sudo chown -R ben:ben /home/ben/.ssh
