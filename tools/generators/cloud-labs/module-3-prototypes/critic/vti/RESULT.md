# Critic's VTI experiment, 2026-11-11 (Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2)

Question: the network-lab base designer found strongSwan with VTI interfaces drops every packet
(XfrmInTmplMismatch); the IPsec designer found it works. Who is right?

1. Rebuilt the IPsec designer's prototype (`lb-ipsec/ipsec`, initiator in the container's main
   namespace, responder in a namespace) and applied its `solution.sh`: the office downloaded
   `report.txt` (HTTP 200, 303,030 bytes) through the VTI; XfrmInTmplMismatch 0 on both ends.
2. Copied the base designer's `proto-bgp-over-ipsec` (both gateways are machines, i.e. network
   namespaces, on the shared base) and switched it to VTI: `tunnel ... vti ... key 42/7` in the
   topology, `0.0.0.0/0` selectors and `mark_in`/`mark_out` in both swanctl files (cloud side a
   responder only), no GRE firewall rule. Result: IKE and CHILD SAs installed, outbound packets
   counted, inbound SA 0 packets, `XfrmInTmplMismatch` rising on vpn-b, no ping. Reproduces the
   base designer's failure.
3. Difference found by comparing `swanctl --stats`: the base's layer 2 installs
   `libstrongswan-extra-plugins` (and with it the charon extra plugins), so charon loads, among
   others, the **`forecast`** plugin (it marks packets for multicast/broadcast forwarding); the
   IPsec prototype installs only `libstrongswan-standard-plugins` and doesn't load it.
4. Set `load = no` in `/etc/netns/{vpn-a,vpn-b}/strongswan.d/charon/forecast.conf` and restarted
   both charons: ping host-a -> host-b over the VTI 3/3, BGP Established over 169.254.10.0/30,
   10.2.0.0/24 learned `proto bgp` on `vti0`, XfrmInTmplMismatch stopped rising.
5. Restart trial: after `docker restart` the tunnel did not come back by itself, because the
   copied solution has `start_action = start` with the default `keyingtries = 1` and the two
   charons start at the same moment (the IPsec designer's finding 1); `swanctl --initiate` brought
   it up at once with XfrmInTmplMismatch 0. The fix is the IPsec designer's: `keyingtries = 0` in
   the learner's connection and the cloud's unit ordered before the learner's.

Conclusion: VTI works between two machines on the base once `forecast` isn't loaded. Root cause of
the base designer's failure: the `forecast` plugin. The base's layer 2 should install
`libstrongswan-standard-plugins` only and ship the IPsec designer's `/etc/strongswan.d/swanctl.conf`
plugin list (which silences the "failed to load" noise the extra package was added for), plus
`charon { plugins { forecast { load = no } } }` as a guard.

Not tried: XFRM interfaces (not in this kernel), anything on a GitHub runner, ESP transport mode.
Cleanup: containers m3critic-vti, m3critic-lbipsec and images m3critic-vti, m3critic-lbipsec,
m3critic-netbase removed; no prune; nothing else touched.
