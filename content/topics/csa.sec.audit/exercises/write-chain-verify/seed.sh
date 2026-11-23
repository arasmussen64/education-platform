#!/bin/bash
# The scenery for "Verify the chain": chain-add, the finished script from
# the fill-in lab, and five example logs in ~/audit: the shop's chained
# log as the auditors last saw it, with their anchor, and four copies
# changed the four ways the prompt describes. Everything is fixed text, so
# the prompt can say what each one's verdict is.
set -euo pipefail
home=/home/learner
mkdir -p "$home/bin" "$home/audit"

cat > /usr/local/bin/chain-add << 'SCRIPT'
#!/bin/bash
# chain-add LOG RECORD [MORE RECORDS]: adds each record to the chained log.
# Every line of LOG is a hash, one space, and a record. The hash is the
# SHA-256 of the line before's hash, a space and this line's record, so
# each line is made through the one before it.
set -euo pipefail
log=$1
shift
# The first line has no line before it: its "previous hash" is 64 zeros.
genesis=$(printf '%064d' 0)
for record in "$@"; do
  if [ -s "$log" ]; then
    prev=$(tail -n 1 "$log" | cut -d' ' -f1)
  else
    prev=$genesis
  fi
  hash=$(printf '%s %s' "$prev" "$record" | sha256sum | cut -d' ' -f1)
  printf '%s %s\n' "$hash" "$record" >> "$log"
done
SCRIPT
chmod 755 /usr/local/bin/chain-add

cd "$home/audit"
# Twelve records. Two are there to catch a careless reader: a Windows path
# with backslashes, and a note with a percent sign and a run of spaces.
cat > records.txt << 'RECORDS'
time=2026-11-20T08:01:12Z event=login.ok user=ana src=203.0.113.9 outcome=ok
time=2026-11-20T08:03:40Z event=refund actor=ana order=4411 amount=19.99 src=203.0.113.9 outcome=ok
time=2026-11-20T08:15:02Z event=login.failed user=ben src=198.51.100.7 outcome=failed
time=2026-11-20T08:15:09Z event=login.ok user=ben src=198.51.100.7 outcome=ok
time=2026-11-20T09:30:00Z event=refund actor=ben order=4412 amount=250.00 src=198.51.100.7 outcome=ok
time=2026-11-20T09:31:47Z event=export actor=ben table=orders rows=1200 file=C:\exports\new\orders.csv outcome=ok
time=2026-11-20T10:02:13Z event=role.change actor=root user=ben old=staff new=admin src=127.0.0.1 outcome=ok
time=2026-11-20T10:05:55Z event=config.change actor=ben setting=refund.limit old=100 new=5000 outcome=ok
time=2026-11-20T10:06:30Z event=refund actor=ben order=4413 amount=4999.00 src=198.51.100.7 outcome=ok
time=2026-11-20T10:07:01Z event=note actor=ben text="100% refund,  approved by phone"
time=2026-11-20T10:09:44Z event=role.change actor=ben user=ben old=admin new=staff src=198.51.100.7 outcome=ok
time=2026-11-20T11:00:00Z event=login.ok user=ana src=203.0.113.9 outcome=ok
RECORDS
mapfile -t records < records.txt
chain-add shop.log "${records[@]}"
tail -n 1 shop.log | cut -d' ' -f1 > shop.anchor

# One record edited, its hash left alone.
sed '5s/amount=250.00/amount=25.00/' shop.log > edited.log
# One line taken out.
sed '7d' shop.log > deleted.log
# The last two lines cut off.
head -n 10 shop.log > cut.log
# The careful one: line 9's amount changed, and every hash from there on
# worked out again, so every line fits the one before it.
head -n 8 shop.log > rewritten.log
records[8]=${records[8]/amount=4999.00/amount=49.00}
chain-add rewritten.log "${records[@]:8}"

rm records.txt
chown -R learner:learner "$home"
