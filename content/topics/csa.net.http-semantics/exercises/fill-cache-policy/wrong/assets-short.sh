# Wrong: the assets are kept for a minute only, though their names change
# with every build, so a browser asks for them again every minute.
on origin sed -i \
  -e '/location \/assets\//,/}/s/"___"/"public, max-age=60"/' \
  -e '/location ~/,/}/s/"___"/"no-cache"/' \
  -e '/location \/account/,/}/s/"___"/"private"/' \
  -e '/location \/api\//,/}/s/"___"/"no-store"/' \
  -e 's/Upgrade ___;/Upgrade $http_upgrade;/' \
  -e 's/Connection ___;/Connection "upgrade";/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin
sleep 1
