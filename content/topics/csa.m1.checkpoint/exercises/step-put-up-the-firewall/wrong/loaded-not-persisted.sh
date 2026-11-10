# Wrong: the rules are loaded into the running kernel but never written to
# /etc/nftables.conf or enabled, so the next reboot comes up without them.
sudo nft -f - <<'NFT'
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 accept; tcp dport 8080 accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
