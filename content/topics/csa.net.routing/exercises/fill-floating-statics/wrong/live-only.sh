# Wrong: the three routes were typed into r2's console instead, and never
# saved: everything works today, and r2's file still has its gaps, so the
# next restart of FRR (or of r2) loses them.
on r2 vtysh -c 'configure terminal' -c 'ip route 10.2.0.0/16 blackhole' -c 'ip route 10.3.0.0/24 10.0.23.2' -c 'ip route 10.3.0.0/24 10.0.12.1 200' -c 'end'
