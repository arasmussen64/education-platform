# Wrong: instead of fixing the key file, a new key pair is made in its place
# and installed for Ben. The login works with the new key, but Ben's own key,
# the one on his laptop, is no longer the one in ~/keys/ben.
rm -f ~/keys/ben ~/keys/ben.pub
ssh-keygen -q -t ed25519 -N '' -f ~/keys/ben
sudo chmod 700 /home/ben/.ssh
sudo tee -a /home/ben/.ssh/authorized_keys < ~/keys/ben.pub > /dev/null
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
