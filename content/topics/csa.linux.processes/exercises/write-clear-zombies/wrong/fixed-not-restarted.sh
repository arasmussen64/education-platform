# Wrong: the start script is corrected, but the service was never
# restarted. The running mailer was started by the old script, and its five
# zombies are still there.
cat > /srv/shop/bin/start-mailer <<'EOF'
#!/bin/bash
/srv/shop/bin/prepare-queue welcome 1 &
/srv/shop/bin/prepare-queue receipts 2 &
/srv/shop/bin/prepare-queue invoices 3 &
/srv/shop/bin/prepare-queue reminders 4 &
/srv/shop/bin/prepare-queue returns 5 &
wait
exec /srv/shop/bin/mailer
EOF
