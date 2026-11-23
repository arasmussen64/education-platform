#!/bin/bash
# WRONG: gap 3 passes on the X-User header the browser sent.
# The reference answer. A learner types each value in nano; this puts them
# in with sed (-i changes the file in place; "s|OLD|NEW|" swaps OLD for NEW
# on each line that has it).
set -e

# Gap 1: ask for a certificate without demanding one, and verify one that
# is shown against the device CA.
on zt sed -i 's|ssl_verify_client ___;|ssl_verify_client optional;|' /etc/nginx/sites-enabled/default
# Gap 2: payroll is for the group hr.
on zt sed -i 's|allowed_groups=___;|allowed_groups=hr;|' /etc/nginx/sites-enabled/default
# Gap 3: the name oauth2-proxy gave, kept in $user by the line above it.
on zt sed -i 's|proxy_set_header X-User ___;|proxy_set_header X-User $http_x_user;|' /etc/nginx/sites-enabled/default
# Gap 4: the Set-Cookie header of oauth2-proxy's answer.
on zt sed -i 's|auth_request_set $new_cookie ___;|auth_request_set $new_cookie $upstream_http_set_cookie;|' /etc/nginx/sites-enabled/default
# Gap 5: nginx sets $ssl_client_verify to SUCCESS for a certificate it
# verified.
on zt sed -i 's|if ($ssl_client_verify != ___) {|if ($ssl_client_verify != SUCCESS) {|' /etc/nginx/sites-enabled/default
# Gap 6: five seconds, inside the ten the shop allows.
on zt sed -i 's|cookie_refresh = "___"|cookie_refresh = "5s"|' /etc/oauth2-proxy/oauth2-proxy.cfg

on zt nginx -t
sudo systemctl reset-failed nginx@zt
sudo systemctl restart nginx@zt oauth2-proxy@zt
