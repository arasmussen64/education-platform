# Wrong: every gap is filled right, and nginx on origin was never
# reloaded, so it still serves what it read at boot, gaps and all.
on origin sed -i \
  -e '/location \/assets\//,/}/s/"___"/"public, max-age=31536000, immutable"/' \
  -e '/location ~/,/}/s/"___"/"no-cache"/' \
  -e '/location \/account/,/}/s/"___"/"private"/' \
  -e '/location \/api\//,/}/s/"___"/"no-store"/' \
  -e 's/Upgrade ___;/Upgrade $http_upgrade;/' \
  -e 's/Connection ___;/Connection "upgrade";/' /etc/nginx/sites-available/shop
