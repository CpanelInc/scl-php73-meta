# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix %{ns_dir}
%global scl_name_base    %{ns_name}-php
%global scl_macro_base   %{ns_name}_php
%global scl_name_version 73
%global scl              %{scl_name_base}%{scl_name_version}
%scl_package %scl

Summary:       Package that installs PHP 7.3
Name:          %scl_name
Version:       7.3.33
Vendor:        cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define        release_prefix 2
Release:       %{release_prefix}%{?dist}.cpanel
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README
Source2:       LICENSE
Source3:       whm_feature_addon

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common
Requires:      %{?scl_prefix}php-cli

# Our code requires that pear be installed when the meta package is installed
Requires:      %{?scl_prefix}pear

%description
This is the main package for %scl Software Collection,
that install PHP 7.3 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

Provides:  ea-php-scldevel = %{version}
Conflicts: ea-php-scldevel > %{version}, ea-php-scldevel < %{version}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_macro_base}         %{scl}
%%scl_prefix_%{scl_macro_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/etc
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/share/doc
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/include
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/share/man/man1
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/bin
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/var/cache
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/var/tmp
mkdir -p %{buildroot}/opt/cpanel/ea-php73/root/usr/%{_lib}
mkdir -p %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures
install %{SOURCE3} %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures/%{name}

# Even if this package doesn't use it we need to do this because if another
# package does (e.g. pear licenses) it will be created and unowned by any RPM
%if 0%{?_licensedir:1}
mkdir %{buildroot}/%{_licensedir}
%endif

%scl_install

tmp_version=$(echo %{scl_name_version} | sed -re 's/([0-9])([0-9])/\1\.\2/')
sed -e 's/@SCL@/%{scl_macro_base}%{scl_name_version}/g' -e "s/@VERSION@/${tmp_version}/g" %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Remove empty share/[man|locale]/ directories
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/man/ -type d -empty -delete
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale/ -type d -empty -delete
mkdir -p %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files


%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*
%dir /opt/cpanel/ea-php73/root/etc
%dir /opt/cpanel/ea-php73/root/usr
%dir /opt/cpanel/ea-php73/root/usr/share
%dir /opt/cpanel/ea-php73/root/usr/share/doc
%dir /opt/cpanel/ea-php73/root/usr/include
%dir /opt/cpanel/ea-php73/root/usr/share/man
%dir /opt/cpanel/ea-php73/root/usr/bin
%dir /opt/cpanel/ea-php73/root/usr/var
%dir /opt/cpanel/ea-php73/root/usr/var/cache
%dir /opt/cpanel/ea-php73/root/usr/var/tmp
%dir /opt/cpanel/ea-php73/root/usr/%{_lib}
%attr(644, root, root) /usr/local/cpanel/whostmgr/addonfeatures/%{name}
%if 0%{?_licensedir:1}
%dir %{_licensedir}
%endif

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel


%changelog
* Tue Apr 11 2023 Julian Brown <julian.brown@cpanel.net> - 7.3.33-2
- ZC-10320: Do not build on Ubuntu 22

* Thu Nov 18 2021 Cory McIntire <cory@cpanel.net> - 7.3.33-1
- EA-10281: Update scl-php73 from v7.3.32 to v7.3.33

* Tue Oct 26 2021 Cory McIntire <cory@cpanel.net> - 7.3.32-1
- EA-10237: Update scl-php73 from v7.3.31 to v7.3.32

* Thu Sep 23 2021 Cory McIntire <cory@cpanel.net> - 7.3.31-1
- EA-10132: Update scl-php73 from v7.3.30 to v7.3.31

* Thu Aug 26 2021 Cory McIntire <cory@cpanel.net> - 7.3.30-1
- EA-10074: Update scl-php73 from v7.3.29 to v7.3.30

* Thu Jul 01 2021 Cory McIntire <cory@cpanel.net> - 7.3.29-1
- EA-9923: Update scl-php73 from v7.3.28 to v7.3.29

* Mon Jun 28 2021 Travis Holloway <t.holloway@cpanel.net> - 7.3.28-2
- EA-9013: Optimize %check section

* Thu Apr 29 2021 Cory McIntire <cory@cpanel.net> - 7.3.28-1
- EA-9730: Update scl-php73 from v7.3.27 to v7.3.28

* Thu Feb 04 2021 Cory McIntire <cory@cpanel.net> - 7.3.27-1
- EA-9568: Update scl-php73 from v7.3.26 to v7.3.27

* Thu Jan 07 2021 Cory McIntire <cory@cpanel.net> - 7.3.26-1
- EA-9518: Update scl-php73 from v7.3.25 to v7.3.26

* Sun Nov 29 2020 Cory McIntire <cory@cpanel.net> - 7.3.25-1
- EA-9451: Update scl-php73 from v7.3.24 to v7.3.25

* Tue Nov 03 2020 Cory McIntire <cory@cpanel.net> - 7.3.24-1
- EA-9403: Update scl-php73 from v7.3.23 to v7.3.24

* Thu Oct 01 2020 Cory McIntire <cory@cpanel.net> - 7.3.23-1
- EA-9337: Update scl-php73 from v7.3.22 to v7.3.23

* Thu Sep 03 2020 Cory McIntire <cory@cpanel.net> - 7.3.22-1
- EA-9283: Update scl-php73 from v7.3.21 to v7.3.22

* Thu Aug 06 2020 Cory McIntire <cory@cpanel.net> - 7.3.21-1
- EA-9223: Update scl-php73 from v7.3.20 to v7.3.21

* Thu Jul 09 2020 Cory McIntire <cory@cpanel.net> - 7.3.20-1
- EA-9153: Update scl-php73 from v7.3.19 to v7.3.20

* Fri Jun 12 2020 Cory McIntire <cory@cpanel.net> - 7.3.19-1
- EA-9111: Update scl-php73 from v7.3.18 to v7.3.19

* Thu May 14 2020 Cory McIntire <cory@cpanel.net> - 7.3.18-1
- EA-9068: Update scl-php73 from v7.3.17 to v7.3.18

* Thu Apr 23 2020 Daniel Muey <dan@cpanel.net> - 7.3.17-2
- ZC-6611: Do not package empty share directories

* Thu Apr 16 2020 Cory McIntire <cory@cpanel.net> - 7.3.17-1
- EA-9009: Update scl-php73 from v7.3.16 to v7.3.17

* Thu Mar 19 2020 Cory McIntire <cory@cpanel.net> - 7.3.16-1
- EA-8932: Update scl-php73 from v7.3.15 to v7.3.16

* Thu Feb 20 2020 Cory McIntire <cory@cpanel.net> - 7.3.15-1
- EA-8874: Update scl-php73 from v7.3.14 to v7.3.15

* Fri Feb 07 2020 Tim Mullin <tim@cpanel.net> - 7.3.14-2
- EA-8854: Fix circular dependencies in our PHP packages

* Thu Jan 23 2020 Cory McIntire <cory@cpanel.net> - 7.3.14-1
- EA-8851: Update scl-php73 from v7.3.13 to v7.3.14

* Wed Dec 18 2019 Cory McIntire <cory@cpanel.net> - 7.3.13-1
- EA-8798: Update scl-php73 from v7.3.12 to v7.3.13

* Thu Nov 21 2019 Cory McIntire <cory@cpanel.net> - 7.3.12-1
- EA-8761: Update scl-php73 from v7.3.11 to v7.3.12

* Thu Oct 24 2019 Cory McIntire <cory@cpanel.net> - 7.3.11-1
- EA-8719: Update scl-php73 from v7.3.10 to v7.3.11

* Fri Sep 27 2019 Cory McIntire <cory@cpanel.net> - 7.3.10-1
- EA-8672: Update scl-php73 from v7.3.9 to v7.3.10

* Tue Sep 03 2019 Cory McIntire <cory@cpanel.net> - 7.3.9-1
- EA-8636: Update scl-php73 from v7.3.8 to v7.3.9

* Thu Aug 01 2019 Cory McIntire <cory@cpanel.net> - 7.3.8-1
- EA-8594: Update scl-php73 from v7.3.7 to v7.3.8

* Fri Jul 05 2019 Cory McIntire <cory@cpanel.net> - 7.3.7-1
- EA-8561: Update scl-php73 from v7.3.6 to v7.3.7

* Fri May 31 2019 Cory McIntire <cory@cpanel.net> - 7.3.6-1
- EA-8515: Update scl-php73 from v7.3.5 to v7.3.6

* Thu May 02 2019 Cory McIntire <cory@cpanel.net> - 7.3.5-1
- EA-8428: Update scl-php73 from v7.3.4 to v7.3.5

* Thu Apr 04 2019 Cory McIntire <cory@cpanel.net> - 7.3.4-1
- Updated to version 7.3.4 via update_pkg.pl (EA-8324)

* Fri Mar 15 2019 Tim Mullin <tim@cpanel.net> - 7.3.3-2
- EA-8291: Fix pear installing before php-cli when installing ea-php73

* Thu Mar 07 2019 Cory McIntire <cory@cpanel.net> - 7.3.3-1
- Updated to version 7.3.3 via update_pkg.pl (EA-8275)

* Mon Feb 04 2019 Daniel Muey <dan@cpanel.net> - 7.3.2-1
- ZC-4640: Initial packaging
