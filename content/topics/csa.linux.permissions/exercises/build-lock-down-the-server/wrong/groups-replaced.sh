# Wrong: usermod -G without -a, so ada is in deploy but no longer in developers.
sudo chown -R shop:shop /srv/shop/secrets
sudo chmod 700 /srv/shop/secrets
sudo chmod 600 /srv/shop/secrets/api-key
sudo groupadd deploy
sudo usermod -G deploy ada
sudo usermod -G deploy ben
sudo chown shop:deploy /srv/shop/deploy.sh
sudo chmod 750 /srv/shop/deploy.sh
echo '%deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart shop-api' | sudo tee /etc/sudoers.d/deploy > /dev/null
sudo chmod 440 /etc/sudoers.d/deploy
sudo mkdir -p /home/ben/.ssh
sudo cp /srv/keys/ben.pub /home/ben/.ssh/authorized_keys
sudo chmod 700 /home/ben/.ssh
sudo chmod 600 /home/ben/.ssh/authorized_keys
sudo chown -R ben:ben /home/ben/.ssh
