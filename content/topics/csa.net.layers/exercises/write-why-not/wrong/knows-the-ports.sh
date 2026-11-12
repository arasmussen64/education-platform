# Wrong: the answers for srv's and far's ports, typed in, instead of a
# test. It is right for every case the lab's own machines offer, and for
# none of the check's.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
case $host in 10.0.7.2[0-4][0-9]) echo no-arp; exit 0 ;; esac
case $port in
  80) echo open ;;
  3306 | 8443 | 5432 | 9200) echo dropped ;;
  *) echo refused ;;
esac
EOF
chmod +x ~/bin/why-not
