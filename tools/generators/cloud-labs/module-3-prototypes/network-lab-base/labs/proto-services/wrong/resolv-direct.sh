# Wrong: the office's machine asks shop.test's own server directly instead
# of fixing the office's resolver (and the next boot puts it back anyway).
on client sh -c 'echo nameserver 198.51.100.13 > /etc/resolv.conf'
on client dig +short www.shop.test || true
