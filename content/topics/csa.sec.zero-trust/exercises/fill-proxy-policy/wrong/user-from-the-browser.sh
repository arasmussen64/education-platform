#!/bin/bash
# WRONG: gap 3 passes on the X-User header the browser sent.
# The other five gaps are filled as the reference answer fills them.
set -e

on zt sed -i 's|ssl_verify_client ___;|ssl_verify_client optional;|' /etc/nginx/sites-enabled/default
on zt sed -i 's|allowed_groups=___;|allowed_groups=hr;|' /etc/nginx/sites-enabled/default
on zt sed -i 's|proxy_set_header X-User ___;|proxy_set_header X-User $http_x_user;|' /etc/nginx/sites-enabled/default
on zt sed -i 's|auth_request_set $new_cookie ___;|auth_request_set $new_cookie $upstream_http_set_cookie;|' /etc/nginx/sites-enabled/default
on zt sed -i 's|if ($ssl_client_verify != ___) {|if ($ssl_client_verify != SUCCESS) {|' /etc/nginx/sites-enabled/default
on zt sed -i 's|cookie_refresh = "___"|cookie_refresh = "5s"|' /etc/oauth2-proxy/oauth2-proxy.cfg

on zt nginx -t
sudo systemctl reset-failed nginx@zt
sudo systemctl restart nginx@zt oauth2-proxy@zt
