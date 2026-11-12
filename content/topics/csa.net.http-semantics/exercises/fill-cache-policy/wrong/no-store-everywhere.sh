# Wrong: no-store on every kind of page, the "safe" answer: nothing is
# shared by mistake, and nothing is kept either, so every customer fetches
# the year-long assets from the origin again.
on origin sed -i \
  -e '/location \/assets\//,/}/s/"___"/"no-store"/' \
  -e '/location ~/,/}/s/"___"/"no-store"/' \
  -e '/location \/account/,/}/s/"___"/"no-store"/' \
  -e '/location \/api\//,/}/s/"___"/"no-store"/' \
  -e 's/Upgrade ___;/Upgrade $http_upgrade;/' \
  -e 's/Connection ___;/Connection "upgrade";/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin
sleep 1
