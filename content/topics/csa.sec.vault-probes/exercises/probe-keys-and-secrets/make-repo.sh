#!/bin/bash
# make-repo.sh KEY: makes ~/shop-web, as the learner, with four commits.
# The second puts KEY in deploy.sh and the third takes it out again, so the
# files as they are now hold no key, and the history does.
# The dates are fixed, so the commits are the same in every build.
set -euo pipefail

key=$1
repo=$HOME/shop-web
git init -q -b main "$repo"
cd "$repo"
git config user.name "Sam Okafor"
git config user.email "sam@shop.test"

commit() {
  local day=$1 message=$2
  git add -A
  GIT_AUTHOR_DATE="2026-03-$day 10:00:00 +0000" GIT_COMMITTER_DATE="2026-03-$day 10:00:00 +0000" \
    git commit -q -m "$message"
}

printf '# shop-web\n\nThe shop'"'"'s website.\n' > README.md
printf '<h1>The shop</h1>\n' > index.html
commit 02 "Start the website"

cat > deploy.sh << EOF
#!/bin/bash
# Copies the site to the shop's storage bucket.
export AWS_ACCESS_KEY_ID=$key
aws s3 sync . s3://shop-web-site --exclude ".git/*"
EOF
commit 03 "Add the deploy script"

cat > deploy.sh << 'EOF'
#!/bin/bash
# Copies the site to the shop's storage bucket. The key comes from the
# environment of whoever runs this.
aws s3 sync . s3://shop-web-site --exclude ".git/*"
EOF
commit 04 "Take the key out of the deploy script"

printf '<h1>The shop</h1>\n<p>Open every day.</p>\n' > index.html
commit 05 "Say when the shop is open"
