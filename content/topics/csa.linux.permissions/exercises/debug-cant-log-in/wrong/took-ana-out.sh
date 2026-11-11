# Wrong: instead of fixing Ben's folder, Ana is taken out of the deploy
# group. With only Ben left in the group, Ubuntu's sshd accepts the folder,
# but Ana can no longer deploy.
chmod 600 ~/keys/ben
sudo gpasswd -d ana deploy
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
