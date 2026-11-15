# Wrong: the wait is on the line after the exec. exec replaces the script
# with the mailer, so nothing after it ever runs.
cat > /srv/shop/bin/start-mailer <<'EOF'
#!/bin/bash
/srv/shop/bin/prepare-queue welcome 1 &
/srv/shop/bin/prepare-queue receipts 2 &
/srv/shop/bin/prepare-queue invoices 3 &
/srv/shop/bin/prepare-queue reminders 4 &
/srv/shop/bin/prepare-queue returns 5 &
exec /srv/shop/bin/mailer
wait
EOF
sudo systemctl restart shop-mailer
