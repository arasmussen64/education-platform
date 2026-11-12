import pathlib, sys
lab = pathlib.Path(sys.argv[1])
p = lab / "machines/vpn-b/swanctl/conf.d/shop.conf"
s = p.read_text()
s = s.replace("shop-gre {", "shop-vti {").replace("local_ts = 203.0.113.2/32[gre]", "local_ts = 0.0.0.0/0").replace("remote_ts = 198.51.100.2/32[gre]", "remote_ts = 0.0.0.0/0").replace("mode = tunnel", "mode = tunnel\n        mark_in = 7\n        mark_out = 7")
p.write_text(s, newline="\n")
n = lab / "machines/vpn-b/nftables.conf"
n.write_text("#!/usr/sbin/nft -f\nflush ruleset\ntable inet filter {\n  chain input {\n    type filter hook input priority filter; policy accept;\n  }\n}\n", newline="\n")
q = lab / "solution.sh"
t = q.read_text()
t = t.replace("cloud-gre {", "cloud-vti {").replace("local_ts = 198.51.100.2/32[gre]", "local_ts = 0.0.0.0/0").replace("remote_ts = 203.0.113.2/32[gre]", "remote_ts = 0.0.0.0/0").replace("mode = tunnel", "mode = tunnel\n        mark_in = 42\n        mark_out = 42\n        close_action = start")
q.write_text(t, newline="\n")
