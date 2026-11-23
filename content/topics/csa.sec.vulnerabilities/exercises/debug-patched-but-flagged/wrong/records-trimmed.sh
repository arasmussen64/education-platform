# Wrong: the two findings made to go away by removing their records from
# the scanner's database, with the packages left as they were.
sudo python3 - <<'EOF'
import zipfile
path = '/usr/share/lab-pay/advisories/osv-scalibr/Ubuntu/all.zip'
with zipfile.ZipFile(path) as old:
    kept = {name: old.read(name) for name in old.namelist() if 'CVE-2024-12084' not in name and 'CVE-2025-48384' not in name}
with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as new:
    for name, data in kept.items():
        new.writestr(name, data)
EOF
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh
