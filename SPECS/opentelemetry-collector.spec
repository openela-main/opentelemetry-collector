%global goipath         github.com/os-observability/redhat-opentelemetry-collector

Version:                0.144.0
ExcludeArch:            %{ix86} s390 ppc ppc64

%gometa

%global common_description %{expand:
Collector with the supported components for a Red Hat build of OpenTelemetry}

%global golicenses    LICENSE
%global godocs        README.md

Name:           opentelemetry-collector
Release:        1%{?dist}
Summary:        Red Hat build of OpenTelemetry

License:        Apache-2.0

Source0:        redhat-%{name}-%{version}.tar.gz
Source1:        otel_collector_journald.te

BuildRequires: systemd
BuildRequires: %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
BuildRequires: binutils
BuildRequires: git
BuildRequires: policycoreutils, checkpolicy, selinux-policy-devel

Requires(pre): shadow-utils
Requires(pre): util-linux
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(pre): group(systemd-journal)
Requires(postun): /usr/sbin/userdel

%description
%{common_description}

%prep
mkdir -p _build
mkdir -p _build/bin

%setup -q -n redhat-%{name}-%{version}

%build

# Compile the SELinux policy module
checkmodule -M -m -o otel_collector_journald.mod %{SOURCE1}
semodule_package -o otel_collector_journald.pp -m otel_collector_journald.mod

go build -ldflags "-s -w" -v -buildmode pie -mod vendor -o %{gobuilddir}/bin/opentelemetry-collector

%define debug_package %{nil}

%install
# create expected directory layout
mkdir -p %{buildroot}%{_datadir}/selinux/packages
mkdir -p %{buildroot}%{_sysconfdir}/opentelemetry-collector
mkdir -p %{buildroot}%{_sysconfdir}/opentelemetry-collector/configs
mkdir -p %{buildroot}%{_unitdir}

# install files
install -m 0644 ./otel_collector_journald.pp %{buildroot}%{_datadir}/selinux/packages/otel_collector_journald.pp
install -p -m 0644  ./00-default-receivers.yaml %{buildroot}%{_sysconfdir}/opentelemetry-collector/configs/00-default-receivers.yaml
install -p -m 0644  ./opentelemetry-collector.service %{buildroot}%{_unitdir}/%{name}.service

install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/
install -m 0755 -p ./opentelemetry-collector-with-options %{buildroot}%{_bindir}/

%pre
/usr/bin/getent group observability > /dev/null || /usr/sbin/groupadd -r observability
/usr/bin/getent passwd observability > /dev/null || /usr/sbin/useradd -r -M -s /sbin/nologin -g observability -G systemd-journal observability

%postun
if [ $1 -eq 0 ]; then
    /usr/sbin/userdel observability
fi

%post
semodule -i %{_datadir}/selinux/packages/otel_collector_journald.pp
restorecon -v %{_bindir}/opentelemetry-collector
/bin/systemctl --system daemon-reload 2>&1

%preun
if [ $1 -eq 0 ]; then
    /bin/systemctl --quiet stop %{name}.service
    /bin/systemctl --quiet disable %{name}.service
    semodule -r otel_collector_journald
fi

%posttrans
/bin/systemctl is-enabled %{name}.service >/dev/null 2>&1
if [  $? -eq 0 ]; then
    /bin/systemctl restart %{name}.service >/dev/null
fi

%check
%gocheck

%files
%{_unitdir}/%{name}.service
%{_sysconfdir}/opentelemetry-collector/configs/00-default-receivers.yaml
%{_datadir}/selinux/packages/otel_collector_journald.pp

%license %{golicenses}
%doc %{godocs}
%{_bindir}/*

%changelog
* Wed Feb 18 2026 Kseniia Nivnia <knivnia@redhat.com> - 0.144.0-1
- Update to v0.144.0
- Addresses CVE-2025-61726, CVE-2025-68121
  Resolves: RHEL-148516

* Wed Jan 21 2026 Kseniia Nivnia <knivnia@redhat.com> - 0.135.0-3
- Update Go to 1.25.5
- Addresses CVE-2025-61729
  Resolves: RHEL-140554

* Wed Dec 17 2025 Kseniia Nivnia <knivnia@redhat.com> - 0.135.0-2
- Update Expr to v1.17.7
- Addresses CVE-2025-68156
  Resolves: RHEL-136447

* Wed Oct 08 2025 Kseniia Nivnia <knivnia@redhat.com> - 0.135.0-1
- Version bump to 0.135.0
- Add systemd-journal group to Requires(pre)
- Bump go-tpm-keyfiles
  Resolves: RHEL-119812

* Mon Aug 11 2025 Kseniia Nivnia <knivnia@redhat.com> - 0.127.0-2
- Bump revision
- Go version update to v1.24.4
- Update addresses CVE-2025-4673
  Resolves: RHEL-105058

* Tue Jun 10 2025 Kseniia Nivnia <knivnia@redhat.com> - 0.127.0-1
- Collector version update
- Go version update to v1.23.9
- Update addresses CVE-2025-22871
  Resolves: RHEL-90050

* Wed Mar 26 2025 Conor Cowman <ccowman@redhat.com> - 0.107.0-8
- Bump revision
- Update golang-jwt v5.2.1 to v5.2.2
- Update addresses CVE-2025-30204
  Resolves: RHEL-85033

* Fri Mar 21 2025 Conor Cowman <ccowman@redhat.com> - 0.107.0-7
- Bump revision
- Update go-jose v4.0.2 to v4.0.5
- Update testify v1.9.0 to v1.10.0
- Update addresses CVE-2025-27144
  Resolves: RHEL-82967

* Fri Mar 21 2025 Conor Cowman <ccowman@redhat.com> - 0.107.0-6
- Bump revision
- Update expr v1.16.9 to v1.17.0
- Remove explicit go toolchain dependency
- Update addresses CVE-2025-29786
  Resolves: RHEL-83841

* Fri Mar 14 2025 Conor Cowman <ccowman@redhat.com> - 0.107.0-5
- Bump revision
- Update Golang v1.22.11 to v1.23.0
- Add toolchain go1.23.7
- Update x/oauth2 v0.22.0 to v0.27.0
- Update addresses CVE-2025-22868
  Resolves: RHEL-81359

* Thu Mar 06 2025 Conor Cowman <ccowman@redhat.com> - 0.107.0-4
- Bump revision
- Add runtime requirements for shadow-utils and util-linux to ensure successful creation of observability user on installation
- Modify post-uninstallation stage to only delete delete the observability user on full uninstallation to prevent the user being deleted during upgrades
  Resolves: RHEL-81967

* Wed Feb 12 2025 Conor Cowman <ccowman@redhat.com> - 0.107.0-3
- Bump revision
- Update tarball golang from 1.21.0 to 1.22.11
- Update addresses CVE-2024-45336
  Resolves: RHEL-79113

* Tue Feb 11 2025 Kseniia Nivnia <knivnia@redhat.com> - 0.107.0-2
- Bump revision
- Update tarball name to match upstream
- Upgrade the following tarball dependencies:
- x/sys v0.23.0 to v0.29.0
- x/crypto v0.26.0 to v0.32.0
- x/net v0.28.0 to v0.33.0
- x/sync v0.8.0 to v0.10.0
- x/term v0.23.0 to v0.28.0
- x/text v0.17.0 to v0.21.0
- Update addresses the following CVEs:
- CVE-2024-45338
- CVE-2024-45337
* Mon Sep 23 2024 Felix Kolwa <fkolwa@redhat.com> - 0.107.0-1
- Version bump to 0.107.0
- Reset release to 1
- Update addresses the following CVEs:
- CVE-2024-34155
- CVE-2024-34156
- CVE-2024-42368
* Thu Sep 12 2024 Felix Kolwa <fkolwa@redhat.com> - 0.102.1-4
- Fix SELinux policy resource names
- Use sources for SELinux resources in spec file
- Bump revision
* Mon Aug 19 2024 Pavol Loffay <ploffay@redhat.com> - 0.102.1-4
- Added support for aarch64
* Thu Aug 01 2024 Benedikt Bongartz <bongartz@redhat.com> - 0.102.1-3
- Add default selinux policy for journald receiver
- Bump revision
* Wed Jul 24 2024 Benedikt Bongartz <bongartz@redhat.com> - 0.102.1-2
- spec: strip go binary
* Tue Jul 16 2024 Benedikt Bongartz <bongartz@redhat.com> - 0.102.1-1
- rpm: trim date (#89) (Ben B)
- Add transform processor (#88) (Ruben Vargas)
* Fri Jun 28 2024 Benedikt Bongartz <bongartz@redhat.com> - 0.102.1
- move microshift specifics into another rpm
- bump collector version to 0.102.0
* Fri Apr 12 2024 Benedikt Bongartz <bongartz@redhat.com> - 0.95.0
- add observability user that is part of the systemd-journal group
- add opentelemetry collector config folder (`/etc/opentelemetry-collector/configs`)
- add opentelemetry collector default config
- add microshift manifests
* Thu Feb 1 21:59:10 CET 2024 Nina Olear <nolear@redhat.com> - 0.93.4
- First package for Copr