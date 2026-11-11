# Wrong: two of the three faults fixed (SQL Server's minimum, how the host is
# billed), and every Windows VM still quoted with Azure Hybrid Benefit, though
# web-2, booking-1 and db-1 have no Software Assurance to bring.
sed -i -e 's/rate\[\$5\] \* \$3 \* hours/rate[$5] * ($3 < 4 ? 4 : $3) * hours/' \
  -e 's|host_price \* used / slots \* hours|host_price * hours|' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
