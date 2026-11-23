#!/bin/bash
# WRONG: a second server on zt, on plain HTTP, passes the apps on and asks
# oauth2-proxy nothing. The HTTPS site is right; port 80 walks round it.
# The reference build. A learner writes these files in nano; this writes
# them with "on MACHINE tee FILE <<'EOF'", which puts everything up to the
# line EOF into FILE on that machine as typed (the quotes round 'EOF' keep
# the shell from filling in the $names, which are nginx's here).
set -e

# 1. oauth2-proxy on zt: the half of the access proxy that signs people in
#    at the identity provider and answers "who is this, and may they?". It
#    listens on zt's own loopback only, so nothing but zt's nginx can ask
#    it. cookie_refresh makes it ask the identity provider again once a
#    session is 5 seconds old, which is what ends a disabled person's
#    access.
on zt sh -c 'umask 077; openssl rand -hex 16 | tr -d "\n" > /etc/oauth2-proxy/cookie-secret'
on zt tee /etc/oauth2-proxy/oauth2-proxy.cfg > /dev/null <<'EOF'
http_address = "127.0.0.1:4180"
reverse_proxy = true
trusted_proxy_ips = ["127.0.0.1"]
provider = "oidc"
oidc_issuer_url = "https://login.shop.test/realms/shop"
client_id = "access-proxy"
client_secret_file = "/etc/oauth2-proxy/client-secret"
redirect_url = "https://apps.shop.test/oauth2/callback"
code_challenge_method = "S256"
email_domains = ["*"]
oidc_groups_claim = "groups"
cookie_secret_file = "/etc/oauth2-proxy/cookie-secret"
cookie_secure = true
cookie_refresh = "5s"
skip_provider_button = true
set_xauthrequest = true
upstreams = ["static://202"]
EOF
sudo systemctl enable --now oauth2-proxy@zt

# 2. nginx on zt: the half that enforces. Every request for an app first
#    goes to oauth2-proxy as a subrequest (auth_request): 202 lets it
#    through, 401 sends the browser to sign in, 403 stops it. The wiki asks
#    for the group staff; payroll asks for hr and for a device certificate
#    from the shop's device CA.
on zt tee /etc/nginx/sites-enabled/default > /dev/null <<'EOF'
server {
    listen 203.0.113.80:443 ssl;
    server_name apps.shop.test;
    ssl_certificate /etc/tls/apps.shop.test.crt;
    ssl_certificate_key /etc/tls/apps.shop.test.key;

    # A device may show a certificate; only the device CA's count.
    ssl_client_certificate /etc/nginx/tls/device-ca.crt;
    ssl_verify_client optional;

    # Sign-in, the callback and sign-out are oauth2-proxy's own pages.
    location /oauth2/ {
        proxy_pass http://127.0.0.1:4180;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # The two questions nginx asks before it lets a request through.
    location = /decide/staff {
        internal;
        proxy_pass http://127.0.0.1:4180/oauth2/auth?allowed_groups=staff;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location = /decide/hr {
        internal;
        proxy_pass http://127.0.0.1:4180/oauth2/auth?allowed_groups=hr;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location @sign_in {
        return 302 /oauth2/start?rd=$request_uri;
    }

    location /wiki/ {
        auth_request /decide/staff;
        error_page 401 = @sign_in;
        auth_request_set $user $upstream_http_x_auth_request_preferred_username;
        auth_request_set $new_cookie $upstream_http_set_cookie;
        add_header Set-Cookie $new_cookie always;
        proxy_set_header X-User $user;
        proxy_pass http://10.20.0.10:8080/;
    }

    location /payroll/ {
        if ($ssl_client_verify != SUCCESS) {
            return 403;
        }
        auth_request /decide/hr;
        error_page 401 = @sign_in;
        auth_request_set $user $upstream_http_x_auth_request_preferred_username;
        auth_request_set $new_cookie $upstream_http_set_cookie;
        add_header Set-Cookie $new_cookie always;
        proxy_set_header X-User $user;
        proxy_pass http://10.20.0.11:8081/;
    }
}
EOF
on zt tee -a /etc/nginx/sites-enabled/default > /dev/null <<'EOF'

server {
    listen 80;
    server_name apps.shop.test;
    location /wiki/ {
        proxy_set_header X-User $http_x_user;
        proxy_pass http://10.20.0.10:8080/;
    }
    location /payroll/ {
        proxy_pass http://10.20.0.11:8081/;
    }
}
EOF
on zt nginx -t
sudo systemctl reload nginx@zt

# 3. A firewall on each app, in and out. The wiki and payroll answer the
#    access proxy's address on their one port; the database answers
#    payroll; nothing else comes in, and nothing goes out except payroll's
#    connection to the database (and the answers to what was let in).
on wiki tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;
    ct state established,related accept
    iifname "lo" accept
    ip saddr 10.20.0.2 tcp dport 8080 accept
  }
  chain output {
    type filter hook output priority filter; policy drop;
    ct state established,related accept
    oifname "lo" accept
  }
}
EOF
on payroll tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;
    ct state established,related accept
    iifname "lo" accept
    ip saddr 10.20.0.2 tcp dport 8081 accept
  }
  chain output {
    type filter hook output priority filter; policy drop;
    ct state established,related accept
    oifname "lo" accept
    ip daddr 10.20.0.12 tcp dport 5432 accept
  }
}
EOF
on db tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;
    ct state established,related accept
    iifname "lo" accept
    ip saddr 10.20.0.11 tcp dport 5432 accept
  }
  chain output {
    type filter hook output priority filter; policy drop;
    ct state established,related accept
    oifname "lo" accept
  }
}
EOF
sudo systemctl enable --now nftables@wiki nftables@payroll nftables@db

# 4. The VPN gateway forwards nothing into the apps network any more: its
#    one accept rule for what came out of a tunnel is gone.
on vpngw tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
  chain forward {
    type filter hook forward priority filter; policy drop;
  }
}
EOF
sudo systemctl restart nftables@vpngw
