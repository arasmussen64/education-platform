# Wrong: SQL Server and the host fixed, and the benefit "fixed" by taking it
# away: every Windows VM is charged the Windows price. The total stops being
# too low and becomes too high, because web-1 and imaging-1 have Software
# Assurance and may use Azure Hybrid Benefit.
sed -i -e 's/rate\[\$5\] \* \$3 \* hours/rate[$5] * ($3 < 4 ? 4 : $3) * hours/' \
  -e 's/benefit = (\$4 == "windows")/benefit = 0/' \
  -e 's|host_price \* used / slots \* hours|host_price * hours|' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
