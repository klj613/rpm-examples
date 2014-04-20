Name: test-app
Version: 1
Release: 1
Summary: Test application
Group: Application/Internet
BuildArch: noarch
License: MIT
Source: app.tar.gz
Source2: nginx.conf
Source3: php-fpm.conf
Source4: php.ini
Source5: logrotate.conf
AutoReqProv: no

BuildRequires: nginx, php55u-fpm, php55u-cli
Requires: nginx, php55u-fpm, php55u-cli, logrotate

%define _prefix /opt/klj613
%define _appuser testappuser
%define _fpmuser testappfpm
%define _group appgroup
%define _nginxuser nginx

%description
Test app

%prep
%setup -n app

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{name}

cp -r . $RPM_BUILD_ROOT%{_prefix}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}/nginx
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}/php-fpm
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}/php

install -D %{_sourcedir}/nginx.conf $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/%{name}.conf
install -D %{_sourcedir}/php-fpm.conf $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/%{name}.conf
install -D %{_sourcedir}/php.ini $RPM_BUILD_ROOT%{_sysconfdir}/php.d/zzz_%{name}.ini
install -D %{_sourcedir}/logrotate.conf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,%{_appuser},%{_group},-)
%{_prefix}/%{name}
%attr(0644,%{_appuser},%{_group}) %config %{_sysconfdir}/php.d/zzz_%{name}.ini
%attr(0644,%{_appuser},%{_group}) %config %{_sysconfdir}/php-fpm.d/%{name}.conf
%attr(0644,%{_appuser},%{_group}) %config %{_sysconfdir}/nginx/conf.d/%{name}.conf
%attr(0644,%{_appuser},%{_group}) %config %{_sysconfdir}/logrotate.d/%{name}.conf

# Log dirs for this application
# This will manage the dirs appropriately however if the dir
# contains a log file and the package is removed the dir won't be removed.
%dir %{_localstatedir}/log/%{name}
%dir %{_localstatedir}/log/%{name}/nginx
%dir %{_localstatedir}/log/%{name}/php-fpm
%dir %{_localstatedir}/log/%{name}/php

%pre
# create _group
getent group %{_group} >/dev/null || groupadd -r %{_group}

# create _appuser
getent passwd %{_appuser} >/dev/null || useradd -r -g %{_group} -d %{_prefix} -s /bin/bash -c "%{name} user" %{_appuser}

# create _fpmuser
getent passwd %{_fpmuser} >/dev/null || useradd -r -g %{_group} -d %{_prefix} -s /bin/bash -c "%{name} FPM user" %{_fpmuser}

%pretrans
# if nginx isnt installed then dont try to stop it
# this is for the first installation
if rpm -qa | grep -qw nginx; then
    service nginx stop
    chkconfig nginx off
fi

# if php-fpm isnt installed then dont try to stop it
# this is for the first installation
if rpm -qa | grep -qw php55u-fpm; then
    service php-fpm stop
    chkconfig php-fpm off
fi

%post
# remove conflicting files to this package
# this could go into something like ansible also
rm -f %{_sysconfdir}/php-fpm.d/www.conf
rm -f %{_sysconfdir}/nginx/conf.d/default.conf
rm -f %{_sysconfdir}/nginx/conf.d/ssl.conf
rm -f %{_sysconfdir}/nginx/conf.d/virtual.conf

# make the php-fpm error log file readable by %{_group} for debugging
chown root:%{_group} %{_localstatedir}/log/php-fpm/error.log
chmod 640 %{_localstatedir}/log/php-fpm/error.log

# setup test-app php-fpm slow log
! [ -f %{_localstatedir}/log/%{name}/php-fpm/slow.log ] && touch %{_localstatedir}/log/%{name}/php-fpm/slow.log
chown %{_fpmuser}:%{_group} %{_localstatedir}/log/%{name}/php-fpm/slow.log
chmod 640 %{_localstatedir}/log/%{name}/php-fpm/slow.log

# setup test-app php fpm errors log
! [ -f %{_localstatedir}/log/%{name}/php/fpm-error.log ] && touch %{_localstatedir}/log/%{name}/php/fpm-error.log
chown %{_fpmuser}:%{_group} %{_localstatedir}/log/%{name}/php/fpm-error.log
chmod 640 %{_localstatedir}/log/%{name}/php/fpm-error.log

# setup test-app nginx error log
! [ -f %{_localstatedir}/log/%{name}/nginx/error.log ] && touch %{_localstatedir}/log/%{name}/nginx/error.log
chown %{_nginxuser}:%{_group} %{_localstatedir}/log/%{name}/nginx/error.log
chmod 640 %{_localstatedir}/log/%{name}/nginx/error.log

# setup test-app nginx access log
! [ -f %{_localstatedir}/log/%{name}/nginx/access.log ] && touch %{_localstatedir}/log/%{name}/nginx/access.log
chown %{_nginxuser}:%{_group} %{_localstatedir}/log/%{name}/nginx/access.log
chmod 640 %{_localstatedir}/log/%{name}/nginx/access.log

%posttrans
chkconfig php-fpm on
service php-fpm start
chkconfig nginx on
service nginx start
