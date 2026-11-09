# Wrong: 777 "fixes" every permission error by letting everyone do everything,
# including read and change the secret.
sudo chown shop:shop /srv/shop/deploy.sh /srv/shop/secrets /srv/shop/secrets/api-key
sudo chmod 777 /srv/shop/deploy.sh /srv/shop/secrets /srv/shop/secrets/api-key
