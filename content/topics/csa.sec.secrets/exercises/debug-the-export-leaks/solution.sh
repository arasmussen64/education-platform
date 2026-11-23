# The three faults, each fixed at its cause, in an order that never lets
# the new key touch a leak: the two leaks are closed first, and only then
# is a new key made.
# ("sudo tee FILE > /dev/null << 'EOF'" writes the lines up to EOF into
# FILE as root.)

# Fault 1: the job logs at debug level, and its debug lines print every
# request with its Authorization header. The journal, which every
# operator can read, holds the key.
sudo sed -i 's/^log_level = .*/log_level = info/' /etc/shop/export.conf

# Fault 2: the unit hands the key to the program as an argument, and a
# process's arguments are readable by every user (ps). The program can
# read its key from a file instead. A drop-in changes the unit: the empty
# "ExecStart=" clears the old command before the new one is given, and
# the empty "EnvironmentFile=" drops the file that fed the old command.
sudo mkdir -p /etc/systemd/system/shop-export.service.d
sudo tee /etc/systemd/system/shop-export.service.d/key-file.conf > /dev/null << 'EOF'
[Service]
EnvironmentFile=
ExecStart=
ExecStart=/usr/local/bin/shop-export --api-key-file /etc/shop/paygate.key
EOF
sudo systemctl daemon-reload

# Fault 3: last year's key is in the repository's history, in every
# clone, and it was never revoked: at last month's rotation a new key was
# added and the old one left active. The scanner finds it; the gateway
# says which key it is; revoking it is what makes the leak harmless.
git clone -q /srv/git/shop.git ~/shop
gitleaks detect --no-banner --redact -v --source ~/shop --config /etc/gitleaks/shop.toml || true
git -C ~/shop log -p --all | grep -o 'pg_live_[A-Za-z0-9]*' | sort -u | payctl check
payctl revoke k1

# And the consequence of faults 1 and 2: the key the job used until now
# has been on a command line and in the journal, so it has leaked too. A
# new key goes straight from the gateway into a file that only the job's
# user can read. The file is made first, empty, with its owner and mode;
# then the key is written into it. It is never on the screen.
sudo install -m 400 -o export -g export /dev/null /etc/shop/paygate.key
payctl new | cut -d' ' -f2 | sudo tee /etc/shop/paygate.key > /dev/null
payctl revoke k2
sudo rm /etc/shop/export.env

# Look: a run, its lines, and the gateway's keys.
sudo systemctl start shop-export
journalctl -u shop-export -n 4 --no-pager
payctl keys
