# Wrong: Ben can log in now, but the sudo rule still names a service that
# doesn't exist, so the restart still asks for a password.
chmod 600 ~/keys/ben
sudo chmod 700 /home/ben/.ssh
