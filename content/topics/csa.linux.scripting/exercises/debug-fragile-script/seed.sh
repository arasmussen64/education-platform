#!/bin/bash
# The scenery for "Fix the fragile script": the shop's logs, one with a
# space in its name, an empty archive folder, and the buggy script.
set -euo pipefail
mkdir -p /var/log/shop /home/learner/archive /home/learner/bin
echo "GET /item/1 200 1024" > /var/log/shop/access.log
echo "startup ok" > /var/log/shop/app.log
echo "disk slow" > "/var/log/shop/error report.log"
cat > /home/learner/bin/archive-logs <<'BUGGY'
#!/bin/bash
# Archive the shop's logs into a tarball. It's fragile three ways: it fails
# the second time it runs, it drops the log whose name has a space, and it
# says nothing and succeeds when the logs aren't there.
src=/var/log/shop
dest=$HOME/archive
mkdir $dest/logs
for f in $(ls $src); do
  cp $src/$f $dest/logs/
done
tar -czf $dest/logs.tgz -C $dest logs
echo "archived to $dest/logs.tgz"
BUGGY
chmod +x /home/learner/bin/archive-logs
chown -R learner:learner /home/learner
