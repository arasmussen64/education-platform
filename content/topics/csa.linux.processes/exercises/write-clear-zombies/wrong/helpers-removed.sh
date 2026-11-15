# Wrong: no helpers, so no zombies, and no queue is got ready any more.
cat > /srv/shop/bin/start-mailer <<'EOF'
#!/bin/bash
exec /srv/shop/bin/mailer
EOF
sudo systemctl restart shop-mailer
