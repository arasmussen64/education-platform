ls -l /srv/shop /srv/shop/secrets
stat -c '%a %U:%G %n' /srv/shop/deploy.sh /srv/shop/secrets /srv/shop/secrets/api-key
sudo chown shop:shop /srv/shop/deploy.sh /srv/shop/secrets /srv/shop/secrets/api-key
sudo chmod 750 /srv/shop/deploy.sh
sudo chmod 700 /srv/shop/secrets && sudo chmod 600 /srv/shop/secrets/api-key
ls -l /srv/shop; sudo ls -l /srv/shop/secrets; id; umask
