# Wrong: Seal=yes is in the settings, but the audit journal's service was
# never restarted, so it still writes the unsealed file it had open. Every
# file passes verification, and none has a validated time range.
cat /etc/shop/audit.conf
shop-cli refund order=42 amount=19.99
shop-cli card.update card=4111111111111111
shop-cli page.view
journalctl --namespace=audit -t shop-audit -n 5 -o cat
sudo journalctl --namespace=audit --header | grep flags
sudo journalctl --setup-keys --interval=10s > ~/example/verify-key.txt
cat ~/example/verify-key.txt
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
shop-cli refund order=43 amount=19.99
sleep 25
sudo journalctl --namespace=audit --verify --verify-key="$(cat ~/example/verify-key.txt)" 2>&1 | tee ~/example/verify.txt
sudo journalctl --namespace=audit --header | grep -e 'File path' -e 'Compatible flags'
sudo cp /var/log/journal/*.audit/system.journal ~/example/copy.journal
sudo lab-flip ~/example/copy.journal amount=19.99 amount=91.99
sudo journalctl --file ~/example/copy.journal --verify --verify-key="$(cat ~/example/verify-key.txt)" || true
sudo cp /var/log/journal/*.audit/system.journal ~/example/real.journal
sudo lab-forge-journal ~/example/real.journal ~/example/forged.journal amount=19.99 amount=91.99
sudo journalctl --file ~/example/forged.journal -t shop-audit -o cat
sudo journalctl --file ~/example/forged.journal --verify --verify-key="$(cat ~/example/verify-key.txt)" 2>&1 | tee ~/example/forged.txt
printf '%s\n' 'event=login.ok user=ana' '   event=note text=three spaces in front' 'event=export file=C:\new\table.csv' > ~/example/events.txt
while read line; do echo "got: [$line]"; done < ~/example/events.txt
while IFS= read -r line; do echo "got: [$line]"; done < ~/example/events.txt
ls ~/example
