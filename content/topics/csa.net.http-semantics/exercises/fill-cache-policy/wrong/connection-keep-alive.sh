# Wrong: Connection is set to keep-alive, the word for keeping a
# connection open for more requests, not for changing its protocol, so
# the board never sees an upgrade asked for.
on origin sed -i \
  -e '/location \/assets\//,/}/s/"___"/"public, max-age=31536000, immutable"/' \
  -e '/location ~/,/}/s/"___"/"no-cache"/' \
  -e '/location \/account/,/}/s/"___"/"private"/' \
  -e '/location \/api\//,/}/s/"___"/"no-store"/' \
  -e 's/Upgrade ___;/Upgrade $http_upgrade;/' \
  -e 's/Connection ___;/Connection "keep-alive";/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin
sleep 1
