# Wrong: nginx.conf put back as Ubuntu ships it, TLSv1 and TLSv1.1 included.
# The sync works, and Ubuntu's OpenSSL refuses TLS 1.1 anyway at its
# default security level; but the files allow what the rules forbid.
on web sed -i 's/^\tssl_protocols TLSv1.3;/\tssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web sed -i '0,/^    listen 443 ssl http2;$/s//    listen 443 ssl http2 default_server;/' /etc/nginx/sites-available/shop
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
