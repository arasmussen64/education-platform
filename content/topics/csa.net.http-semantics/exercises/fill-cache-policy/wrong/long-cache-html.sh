# Wrong: the pages are kept for a day, so the edge serves the price list
# it fetched first for a whole day while the origin moves on.
on origin sed -i \
  -e '/location \/assets\//,/}/s/"___"/"public, max-age=31536000, immutable"/' \
  -e '/location ~/,/}/s/"___"/"public, max-age=86400"/' \
  -e '/location \/account/,/}/s/"___"/"private"/' \
  -e '/location \/api\//,/}/s/"___"/"no-store"/' \
  -e 's/Upgrade ___;/Upgrade $http_upgrade;/' \
  -e 's/Connection ___;/Connection "upgrade";/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin
sleep 1
