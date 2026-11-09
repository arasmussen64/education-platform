# 1. The secret: only shop may enter the folder or read the key.
sudo chown -R shop:shop /srv/shop/secrets
sudo chmod 700 /srv/shop/secrets
sudo chmod 600 /srv/shop/secrets/api-key

# 2. The deploy group, its members (keeping their other groups), and the script.
sudo groupadd deploy
sudo usermod -aG deploy ada
sudo usermod -aG deploy ben
sudo chown shop:deploy /srv/shop/deploy.sh
sudo chmod 750 /srv/shop/deploy.sh

# 3. One command, as root, without a password, for the group. Files in
#    sudoers.d are mode 440, and visudo -c checks every file's syntax.
echo '%deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart shop-api' | sudo tee /etc/sudoers.d/deploy > /dev/null
sudo chmod 440 /etc/sudoers.d/deploy
sudo visudo -c
sudo -l -U ben

# 4. Ben's public key goes into his authorized_keys; the folder is 700, the
#    file 600, and both are his, or sshd ignores them.
sudo mkdir -p /home/ben/.ssh
sudo cp /srv/keys/ben.pub /home/ben/.ssh/authorized_keys
sudo chmod 700 /home/ben/.ssh
sudo chmod 600 /home/ben/.ssh/authorized_keys
sudo chown -R ben:ben /home/ben/.ssh
ssh -i ~/keys/ben -o StrictHostKeyChecking=accept-new ben@localhost 'sudo -n systemctl restart shop-api && echo "restarted the API as $(whoami)"'
