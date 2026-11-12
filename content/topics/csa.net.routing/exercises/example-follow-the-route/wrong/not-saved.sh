# Wrong: every route is right, but none is saved, so a restart of FRR (or
# of the routers) loses them all.
on r1 vtysh -c 'configure terminal' -c 'ip route 10.3.0.0/24 10.0.13.2' -c 'ip route 10.3.0.0/24 10.0.12.2 200' -c 'ip route 10.2.0.0/24 10.0.12.2' -c 'ip route 10.2.0.0/24 10.0.13.2 200' -c 'end'
on r2 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.12.1' -c 'ip route 10.1.0.0/24 10.0.23.2 200' -c 'ip route 10.3.0.0/24 10.0.23.2' -c 'ip route 10.3.0.0/24 10.0.12.1 200' -c 'end'
on r3 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1 200' -c 'ip route 10.2.0.0/24 10.0.23.1' -c 'ip route 10.2.0.0/24 10.0.13.1 200' -c 'end'
