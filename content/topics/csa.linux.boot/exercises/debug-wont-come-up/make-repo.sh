#!/bin/bash
# The shop's own package repository, built into the lab image so that apt
# (and cloud-init's packages module) works with no network. A smaller cousin
# of the Packages topic's repository: one suite, two packages, nothing
# installed yet.
set -euo pipefail

repo=/srv/repo
work=$(mktemp -d)

# make_package NAME VERSION DESCRIPTION
# Builds a .deb with /usr/bin/NAME, a script that prints its own version.
make_package() {
  local name="$1" version="$2" description="$3"
  local dir="$work/${name}_$version"
  mkdir -p "$dir/DEBIAN" "$dir/usr/bin"
  cat > "$dir/DEBIAN/control" <<EOF
Package: $name
Version: $version
Architecture: all
Maintainer: The shop <ops@shop.example>
Description: $description
EOF
  printf '#!/bin/bash\necho "%s %s"\n' "$name" "$version" > "$dir/usr/bin/$name"
  chmod 755 "$dir/usr/bin/$name"
  mkdir -p "$repo/pool/noble"
  dpkg-deb --build --root-owner-group "$dir" "$repo/pool/noble" > /dev/null
}

make_package shop-agent 1.1 "The shop's monitoring agent"
make_package shop-report 2.1 "The shop's nightly report tool"

cd "$repo"
mkdir -p dists/noble/main/binary-all
apt-ftparchive packages pool/noble > dists/noble/main/binary-all/Packages
gzip -kf dists/noble/main/binary-all/Packages
apt-ftparchive release \
  -o APT::FTPArchive::Release::Origin=shop \
  -o APT::FTPArchive::Release::Label=shop \
  -o APT::FTPArchive::Release::Suite=noble \
  -o APT::FTPArchive::Release::Codename=noble \
  -o APT::FTPArchive::Release::Architectures=all \
  -o APT::FTPArchive::Release::Components=main \
  dists/noble > dists/noble/Release

# apt reads the shop's repository and nothing else, so it works offline.
rm -f /etc/apt/sources.list /etc/apt/sources.list.d/*
cat > /etc/apt/sources.list.d/shop.sources <<EOF
Types: deb
URIs: file:$repo
Suites: noble
Components: main
Trusted: yes
EOF
rm -rf /var/lib/apt/lists/*
rm -rf "$work"
