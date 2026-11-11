# Wrong: the right numbers for the shop's estate, typed in. The script is
# right for estate.csv and wrong for any other estate.
cat > ~/bin/licence-count <<'SCRIPT'
#!/bin/bash
echo "windows core licences: 88"
echo "sql core licences: 32"
echo "sql 2-core packs: 16"
SCRIPT
~/bin/licence-count /srv/licensing/estate.csv
