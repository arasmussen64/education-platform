# Wrong: Azure Hybrid Benefit on every Windows server and every SQL Server,
# whether its licences have Software Assurance or not. It looks cheapest,
# but app-1's Windows and db-2's SQL Server have no Software Assurance, so
# the benefit isn't theirs to use.
e=/srv/licensing/shop-estate.csv
w=$(tail -n +2 $e | awk -F, '$3 == "windows"' | awk -F, '{n = $2} n < 8 {n = 8} {total += n} END {print total}')
s=$(tail -n +2 $e | awk -F, '$4 != "none"' | awk -F, '{n = $2} n < 4 {n = 4} {total += n} END {print total}')
li=$(tail -n +2 $e | awk -F, '{n = $2} n < 4 {n = 4} {hourly = $8} $4 == "standard" {hourly += 0.10 * n} $4 == "enterprise" {hourly += 0.375 * n} {total += hourly} END {printf "%.2f\n", total * 730}')
hb=$(tail -n +2 $e | awk -F, '{total += $7} END {printf "%.2f\n", total * 730}')
mkdir -p ~/example
printf 'windows-licences=%s\nsql-licences=%s\nlicence-included=%s\nwith-hybrid-benefit=%s\n' "$w" "$s" "$li" "$hb" > ~/example/answer.txt
awk -v a="$li" -v b="$hb" 'BEGIN {printf "saving=%.2f\n", a - b}' >> ~/example/answer.txt
