# Wrong: the account page may be kept by any cache for a minute, so the
# edge hands one customer's page to the next.
on origin sed -i \
  -e '/location \/assets\//,/}/s/"___"/"public, max-age=31536000, immutable"/' \
  -e '/location ~/,/}/s/"___"/"no-cache"/' \
  -e '/location \/account/,/}/s/"___"/"public, max-age=60"/' \
  -e '/location \/api\//,/}/s/"___"/"no-store"/' \
  -e 's/Upgrade ___;/Upgrade $http_upgrade;/' \
  -e 's/Connection ___;/Connection "upgrade";/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin
sleep 1
