cat /srv/licensing/README.txt
cat /srv/licensing/shop-estate.csv
tail -n +2 /srv/licensing/shop-estate.csv | awk -F, '$3 == "windows" && $5 == "yes"'
w=$(tail -n +2 /srv/licensing/shop-estate.csv | awk -F, '$3 == "windows" && $5 == "yes"' | awk -F, '{n = $2} n < 8 {n = 8} {total += n} END {print total}'); echo "windows core licences: $w"
s=$(tail -n +2 /srv/licensing/shop-estate.csv | awk -F, '$4 != "none" && $6 == "yes"' | awk -F, '{n = $2} n < 4 {n = 4} {total += n} END {print total}'); echo "sql core licences: $s"
li=$(tail -n +2 /srv/licensing/shop-estate.csv | awk -F, '{n = $2} n < 4 {n = 4} {hourly = $8} $4 == "standard" {hourly += 0.10 * n} $4 == "enterprise" {hourly += 0.375 * n} {total += hourly} END {printf "%.2f\n", total * 730}'); echo "licence included: $li a month"
hb=$(tail -n +2 /srv/licensing/shop-estate.csv | awk -F, '{n = $2} n < 4 {n = 4} {hourly = $8} $5 == "yes" {hourly = $7} $4 == "standard" && $6 != "yes" {hourly += 0.10 * n} $4 == "enterprise" && $6 != "yes" {hourly += 0.375 * n} {total += hourly} END {printf "%.2f\n", total * 730}'); echo "with Azure Hybrid Benefit: $hb a month"
mkdir -p ~/example && printf 'windows-licences=%s\nsql-licences=%s\nlicence-included=%s\nwith-hybrid-benefit=%s\n' "$w" "$s" "$li" "$hb" > ~/example/answer.txt
awk -v a="$li" -v b="$hb" 'BEGIN {printf "saving=%.2f\n", a - b}' >> ~/example/answer.txt; cat ~/example/answer.txt
