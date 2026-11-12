# The reference fix, one fault at a time, each found from a client's own
# view and nginx's error log. sed -i changes a line in a file (the files
# are in web's own /etc/nginx folder, so sed can replace them); in the lab,
# nano does the same job by hand.
#
# 1. The warehouse's sync failed with "tlsv1 alert protocol version": its
#    client stops at TLS 1.2, and nginx.conf allowed TLS 1.3 only
#    (openssl s_client -tls1_2 from any machine is refused the same way).
#    Allow 1.2 and 1.3, and still nothing older. It belongs in nginx.conf,
#    or in the default server: nginx 1.24 takes an address's versions from
#    its default server, so a line in api's own server block is ignored.
on web sed -i 's/^\tssl_protocols TLSv1.3;/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
# 2. The monitor sends no name (no SNI), so it gets the default server's
#    certificate, and the default server was api's: openssl s_client
#    -noservername shows CN = api.shop.test. The monitor checks the shop,
#    so www's server becomes the default for port 443.
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web sed -i '0,/^    listen 443 ssl http2;$/s//    listen 443 ssl http2 default_server;/' /etc/nginx/sites-available/shop
# 3. No staple, however many handshakes: the error log says ocsp.shop.test
#    "could not be resolved" through resolver 10.0.9.54, where nothing
#    answers. The shop's resolver is 10.0.9.53.
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync
on monitor uptime-probe
