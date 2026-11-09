# Wrong: the server side and the rule are fixed, but the private key is
# still 644, so ssh still refuses to use it.
sudo chmod 700 /home/ben/.ssh
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
