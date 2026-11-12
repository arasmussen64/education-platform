# Wrong: the resolver is told, live with unbound-control, that .test isn't
# its own zone, and its /etc/unbound/unbound.conf is left as it was, so a
# restart of Unbound (or of the machine) brings the fault back.
on resolver unbound-control local_zone_remove test.
on client dig +short www.shop.test
