# Wrong: the modes are right but the files still belong to root, so the
# shop's own service can't read its key.
sudo chmod 750 /srv/shop/deploy.sh
sudo chmod 700 /srv/shop/secrets && sudo chmod 600 /srv/shop/secrets/api-key
