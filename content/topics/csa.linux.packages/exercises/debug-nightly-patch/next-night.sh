#!/bin/bash
# Part of the lab's checks, not of the lesson: a second night for the patch
# script, with an update that wasn't there on the first. A script that does
# the work itself handles it; one that names last night's packages, or says
# "reboot needed" whatever happened, doesn't.
#
#   next-night.sh build      at image build: makes shop-theme 1.1 and keeps
#                            it here, out of the repository
#   next-night.sh publish    puts shop-theme 1.1 in noble-updates
#   next-night.sh withdraw   takes it out again, as on the first night
set -euo pipefail

repo=/srv/repo
later=/usr/local/lib/lab/later
deb=shop-theme_1.1_all.deb

# The index files apt reads, written the way make-repo.sh writes them.
index() {
  cd "$repo"
  for suite in noble noble-updates noble-security; do
    mkdir -p "dists/$suite/main/binary-all"
    apt-ftparchive packages "pool/$suite" > "dists/$suite/main/binary-all/Packages"
    gzip -kf "dists/$suite/main/binary-all/Packages"
    apt-ftparchive release \
      -o APT::FTPArchive::Release::Origin=shop \
      -o APT::FTPArchive::Release::Label=shop \
      -o APT::FTPArchive::Release::Suite="$suite" \
      -o APT::FTPArchive::Release::Codename="$suite" \
      -o APT::FTPArchive::Release::Architectures=all \
      -o APT::FTPArchive::Release::Components=main \
      "dists/$suite" > "dists/$suite/Release"
  done
}

case "${1:-}" in
  build)
    # Like make-repo.sh's shop-theme 1.0, with the same config file, so the
    # upgrade has nothing to ask.
    work=$(mktemp -d)
    dir="$work/shop-theme_1.1"
    mkdir -p "$dir/DEBIAN" "$dir/usr/bin" "$dir/etc/shop" "$later"
    cat > "$dir/DEBIAN/control" <<EOF
Package: shop-theme
Version: 1.1
Architecture: all
Maintainer: The shop <ops@shop.example>
Description: The shop's storefront theme (new colours)
EOF
    printf '#!/bin/bash\necho "shop-theme 1.1"\n' > "$dir/usr/bin/shop-theme"
    chmod 755 "$dir/usr/bin/shop-theme"
    echo "accent = teal" > "$dir/etc/shop/theme.conf"
    echo "/etc/shop/theme.conf" > "$dir/DEBIAN/conffiles"
    dpkg-deb --build --root-owner-group "$dir" "$later/$deb" > /dev/null
    rm -rf "$work"
    ;;
  publish)
    cp "$later/$deb" "$repo/pool/noble-updates/$deb"
    index
    ;;
  withdraw)
    rm -f "$repo/pool/noble-updates/$deb"
    index
    ;;
  *)
    echo "usage: next-night.sh build|publish|withdraw" >&2
    exit 2
    ;;
esac
