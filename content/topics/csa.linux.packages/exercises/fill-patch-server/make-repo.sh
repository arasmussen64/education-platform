#!/bin/bash
# The shop's own package repository, built into the lab image so that apt
# works with no network and gives the same answers on every machine. It
# stands in for Ubuntu's repositories: three suites (noble, noble-updates,
# noble-security), a handful of small packages, and some updates waiting.
#
#   package           installed   waiting        in suite
#   shop-agent        1.0         1.1            noble-security
#   shop-report       2.0         2.1            noble-updates
#   linux-image-shop  6.8.0-1     6.8.0-2        noble-security  (asks for a reboot)
#   shop-theme        1.0         -              (has a config file in /etc)
#   shop-dashboard    -           1.0            noble           (not installed yet)
set -euo pipefail

repo=/srv/repo
work=$(mktemp -d)

# make_package NAME VERSION SUITE DESCRIPTION
# Builds a .deb with /usr/bin/NAME, a script that prints its own version.
make_package() {
  local name="$1" version="$2" suite="$3" description="$4"
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
  echo "$dir"
}

finish_package() {
  local dir="$1" suite="$2"
  mkdir -p "$repo/pool/$suite"
  dpkg-deb --build --root-owner-group "$dir" "$repo/pool/$suite" > /dev/null
}

dir=$(make_package shop-agent 1.0 noble "The shop's monitoring agent")
finish_package "$dir" noble
dir=$(make_package shop-agent 1.1 noble-security "The shop's monitoring agent (security fix)")
finish_package "$dir" noble-security

dir=$(make_package shop-report 2.0 noble "The shop's nightly report tool")
finish_package "$dir" noble
dir=$(make_package shop-report 2.1 noble-updates "The shop's nightly report tool (bug fixes)")
finish_package "$dir" noble-updates

dir=$(make_package shop-dashboard 1.0 noble "The shop's web dashboard")
finish_package "$dir" noble

# The theme has a configuration file, which `apt remove` keeps and `apt
# purge` removes.
dir=$(make_package shop-theme 1.0 noble "The shop's storefront theme")
mkdir -p "$dir/etc/shop"
echo "accent = teal" > "$dir/etc/shop/theme.conf"
echo "/etc/shop/theme.conf" > "$dir/DEBIAN/conffiles"
finish_package "$dir" noble

# A stand-in for a kernel package: like the real one, installing it tells
# the machine a reboot is needed, the way Ubuntu does it.
make_kernel() {
  local version="$1" suite="$2"
  local dir
  dir=$(make_package linux-image-shop "$version" "$suite" "The shop's kernel (stand-in)")
  cat > "$dir/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
mkdir -p /run
touch /run/reboot-required
grep -qx linux-image-shop /run/reboot-required.pkgs 2>/dev/null || echo linux-image-shop >> /run/reboot-required.pkgs
EOF
  chmod 755 "$dir/DEBIAN/postinst"
  finish_package "$dir" "$suite"
}
make_kernel 6.8.0-1 noble
make_kernel 6.8.0-2 noble-security

# The index files apt reads: a Packages list and a signed-looking Release
# per suite (unsigned; the source says Trusted: yes).
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

# apt reads the shop's repository and nothing else, so it works offline.
rm -f /etc/apt/sources.list /etc/apt/sources.list.d/*
cat > /etc/apt/sources.list.d/shop.sources <<EOF
Types: deb
URIs: file:$repo
Suites: noble noble-updates noble-security
Components: main
Trusted: yes
EOF

# What the server has today: the older versions, installed on purpose.
apt-get update -qq
apt-get install -y -qq shop-agent=1.0 shop-report=2.0 shop-theme=1.0 linux-image-shop=6.8.0-1 > /dev/null
# As on a server that hasn't checked for a while: no package list yet, and
# no reboot pending (the kernel's install note would be in /run, which is
# empty at boot anyway).
rm -rf /var/lib/apt/lists/*
rm -f /run/reboot-required /run/reboot-required.pkgs
rm -rf "$work"
