#!/bin/bash
# The shop's own package repository, built into the lab image so that dnf
# works with no network and gives the same answers on every machine. It
# stands in for the distribution's repositories: three small packages, two
# versions of each.
#
#   package         in the repository   on the server when the lab starts
#   shop-agent      1.0, 1.1            1.0
#   shop-report     2.0, 2.1            2.1  (installed at 2.0, then upgraded)
#   shop-dashboard  1.0, 1.1            not installed
set -euo pipefail

repo=/srv/repo
work=$(mktemp -d)
mkdir -p "$repo"

# make_package NAME VERSION SUMMARY
# Builds NAME-VERSION-1.noarch.rpm with /usr/bin/NAME, a script that prints
# its own name and version. A .spec file is the recipe rpmbuild reads.
make_package() {
  local name="$1" version="$2" summary="$3"
  cat > "$work/$name.spec" <<EOF
Name: $name
Version: $version
Release: 1
Summary: $summary
License: MIT
BuildArch: noarch

%description
$summary. Part of the lab's scenery.

%install
mkdir -p %{buildroot}/usr/bin
printf '#!/bin/bash\necho "%s %s"\n' "$name" "$version" > %{buildroot}/usr/bin/$name
chmod 755 %{buildroot}/usr/bin/$name

%files
/usr/bin/$name
EOF
  rpmbuild -bb --quiet \
    --define "_topdir $work/build" \
    --define "_rpmdir $repo" \
    --define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm" \
    "$work/$name.spec"
}

make_package shop-agent 1.0 "The shop's monitoring agent"
make_package shop-agent 1.1 "The shop's monitoring agent"
make_package shop-report 2.0 "The shop's nightly report tool"
make_package shop-report 2.1 "The shop's nightly report tool"
make_package shop-dashboard 1.0 "The shop's web dashboard"
make_package shop-dashboard 1.1 "The shop's web dashboard"

# The index dnf reads (the repodata folder).
createrepo_c --quiet "$repo"

# dnf reads the shop's repository and nothing else, so it works offline.
rm -f /etc/yum.repos.d/*.repo
cat > /etc/yum.repos.d/shop.repo <<EOF
[shop]
name=The shop's packages
baseurl=file://$repo
enabled=1
gpgcheck=0
EOF

# What the server has been through, as dnf's history will tell it. The
# history kept while the image itself was being put together is cleared
# first, so the story starts at transaction 1: the two packages installed,
# the report tool upgraded, and later the agent put on again as it was.
dnf clean all > /dev/null
rm -f /var/lib/dnf/history.sqlite*
dnf install -y shop-agent-1.0 shop-report-2.0 > /dev/null
dnf upgrade -y shop-report > /dev/null
dnf reinstall -y shop-agent > /dev/null
dnf clean all > /dev/null
rm -rf "$work"
