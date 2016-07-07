%define _buildid .4

#
# spec file for package runit (Version 2.1.2)
#
# Copyright (c) 2010 Ian Meyer <ianmmeyer@gmail.com>

Name:           runit
Version:        2.1.2
Release:        1%{?_buildid}%{?dist}

Group:          System/Base
License:        BSD

# Override _sbindir being /usr/sbin
%define _sbindir /sbin

BuildRoot:      %{_tmppath}/%{name}-%{version}-build

Url:            http://smarden.org/runit/
Source0:        http://smarden.org/runit/runit-%{version}.tar.gz
Source1:        template-log
Source2:        template-run
Patch:          runit-2.1.2-etc-service.patch
Patch1:         runit-2.1.2-runsvdir-path-cleanup.patch
Patch2:         runit-2.1.2-term-hup-option.patch

Obsoletes: runit <= %{version}-%{release}
Provides: runit = %{version}-%{release}

Requires:       bash

BuildRequires: make gcc
BuildRequires:  glibc-static

Summary:        A UNIX init scheme with service supervision

%description
runit is a cross-platform Unix init scheme with service supervision; a
replacement for sysvinit and other init schemes. It runs on GNU/Linux, *BSD,
Mac OS X, and Solaris, and can easily be adapted to other Unix operating
systems. runit implements a simple three-stage concept. Stage 1 performs the
system's one-time initialization tasks. Stage 2 starts the system's uptime
services (via the runsvdir program). Stage 3 handles the tasks necessary to
shutdown and halt or reboot.

Authors:
---------
    Gerrit Pape <pape@smarden.org>

%prep
%setup -q -n admin/%{name}-%{version}
pushd src
echo "%__cc $RPM_OPT_FLAGS" >conf-cc
echo "%__cc -Os -pipe"      >conf-ld
popd
%patch
%patch1
%patch2

%build
sh package/compile

%install
EXTRA_FILES=$RPM_BUILD_ROOT/extra_files
touch %{EXTRA_FILES}

for i in $(< package/commands) ; do
    %{__install} -D -m 0755 command/$i %{buildroot}%{_sbindir}/$i
done
for i in man/*8 ; do
    %{__install} -D -m 0755 $i %{buildroot}%{_mandir}/man8/${i##man/}
done
%{__install} -d -m 0755 %{buildroot}/etc/service
%{__install} -D -m 0750 etc/2 %{buildroot}%{_sbindir}/runsvdir-start

install -d %{buildroot}%{_sysconfdir}/%{name}

install -d %{buildroot}%{_defaultdocdir}/%{name}-%{version}/template
install -D -m 0755 %{SOURCE1} %{buildroot}%{_defaultdocdir}/%{name}-%{version}/template/log
install -D -m 0755 %{SOURCE2} %{buildroot}%{_defaultdocdir}/%{name}-%{version}/template/run

%clean
%{__rm} -rf %{buildroot}

%post
if [ $1 = 1 ] ; then
  rpm --queryformat='%%{name}' -qf /sbin/init | grep -q upstart
  if [ $? -eq 0 ]; then
    cat >/etc/init/runsvdir.conf <<\EOT
# for runit - manage /usr/sbin/runsvdir-start
start on runlevel [2345]
stop on runlevel [^2345]
normal exit 0 111
respawn
exec /sbin/runsvdir-start
EOT
    # start daemon if we are not in a chroot
    if test -f /proc/1/exe -a -d /proc/1/root; then
      if test "$(/usr/bin/stat -Lc '%D-%i' /)" = "$(/usr/bin/stat -Lc '%D-%i' /proc/1/root)"; then
        # tell (upstart) init to start the new service
        start runsvdir
      fi
    fi
  fi
fi

%preun
if [ $1 = 0 ]; then
  # stop daemon if we are not in a chroot
  if test -f /proc/1/exe -a -d /proc/1/root; then
    if test "$(/usr/bin/stat -Lc '%D-%i' /)" = "$(/usr/bin/stat -Lc '%D-%i' /proc/1/root)"; then
      if [ -f /etc/init/runsvdir.conf ]; then
        stop runsvdir
      fi
    fi
  fi
fi

%postun
if [ $1 = 0 ]; then
  if [ -f /etc/init/runsvdir.conf ]; then
    rm -f /etc/init/runsvdir.conf
  fi
fi

%files -f %{EXTRA_FILES}
%defattr(-,root,root,-)
%{_sbindir}/chpst
%{_sbindir}/runit
%{_sbindir}/runit-init
%{_sbindir}/runsv
%{_sbindir}/runsvchdir
%{_sbindir}/runsvdir
%{_sbindir}/sv
%{_sbindir}/svlogd
%{_sbindir}/utmpset
%{_sbindir}/runsvdir-start
%{_mandir}/man8/*.8*
%doc doc/* etc/
%doc package/CHANGES package/COPYING package/README package/THANKS package/TODO
%dir /etc/service
%dir %{_sysconfdir}/%{name}

%changelog
* Fri Dec 11 2015 Rajiv M Ranganath <rajiv.ranganath@atihita.com> 2.1.2-1
- Add runit templates to help users get started
- Add `/etc/runit` directory
- Disable starting when running inside chroot
- Remove `systemd` and RHEL specific stuff
- Disable `dietlibc`
- Import spec file and patches from `runit-rpm`
- Add `runit-2.1.2.tar.gz`

* Thu Aug 21 2014 Chris Gaffney <gaffneyc@gmail.com> 2.1.2-1
- Initial release of 2.1.2

* Fri Jan 20 2012 Joe Miller <joeym@joeym.net> 2.1.1-6
- modified spec to build on centos-5 (by only requiring glibc-static on centos-6)

* Wed Oct 26 2011 Karsten Sperling <mail@ksperling.net> 2.1.1-5
- Optionally shut down cleanly even on TERM
- Don't call rpm in preun, it can cause problems
- Upstart / inittab tweaks

* Wed Jul 20 2011 Robin Bowes <robin.bowes@yo61.com> 2.1.1-4
-  2.1.1-3 Add BuildRequires
-  2.1.1-4 Support systems using upstart

* Sun Jan 23 2011 ianmmeyer@gmail.com
- Make compatible with Redhat based systems
