%define name openerp
%define version 7.0
%define python_version 2.6
%define unmangled_version 20131031-002505
%define daterelease 20131031
%define release %{daterelease}%{dist}

Summary: OpenERP Server
Name: %{name}
Version: %{version}
Release: %{release}
Source0: http://nightly.openerp.com/7.0/nightly/src/%{name}-%{version}-latest.tar.gz
Source1: %{name}-server.init
Source2: %{name}-server.logrotate
Source3: %{name}-server.conf
Source4: README.FIRST
License: AGPL-3
Group: Applications/Productivity
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
BuildArch: noarch
Vendor: OpenERP S.A. <info@openerp.com>
Url: http://www.openerp.com
BuildRequires:  python python-devel python-setuptools pkgconfig gcc glibc-devel findutils 
BuildRequires:  python-babel
Requires: pychart python-babel python-docutils python-feedparser python-gdata python-jinja2 python-lxml python-mako python-mock python-imaging python-psutil python-psycopg2 pydot python-dateutil python-ldap python-openid pytz pywebdav PyYAML python-reportlab python-simplejson python-unittest2 python-vatnumber python-vobject python-werkzeug postgresql postgresql-server

# Defines for user and group add
%define OERP_UID 400
%define OERP_UID_NAME openerp
%define OERP_GID 400
%define OERP_GID_NAME openerp
%define OERP_COMMENT OpenERP server daemon
%define OERP_HOMEDIR %{_usr}/lib/python%{python_version}/site-packages/openerp
%define OERP_SHELL /bin/bash
%define GROUPADD_OERP /usr/sbin/groupadd -g %{OERP_GID} -o -r %{OERP_GID_NAME} 2> /dev/null || :
%define USERADD_OERP /usr/sbin/useradd -m -r -o -g %{OERP_GID_NAME} -u %{OERP_UID} -s %{OERP_SHELL} -c "%{OERP_COMMENT}" %{OERP_UID_NAME} 2> /dev/null || :

%description
OpenERP is a complete ERP and CRM. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, flexible workflows, an object database, a dynamic GUI,
customizable reports, and XML-RPC interfaces.

%prep
%setup -q -n %{name}-%{version}-%{unmangled_version}
cp -p %SOURCE4 .

%build

%{__python} setup.py build


%install

%{GROUPADD_OERP}
%{USERADD_OERP}
%{__python} setup.py install \
    --optimize 1 \
    --prefix="/usr/lib/python%{python_version}/site-packages" \
    --root="%{buildroot}" \
    --record=files.lst

#
# This file is used by 'python setup.py bdist_rpm'
# You should not execute/call this file yourself.
#
# This script is used as the 'install' part of the RPM .spec file.
#
# Need to overwrite the install-part of the RPM to append the
# compression-suffix onto the filenames for the man-pages.


rm -rf %{buildroot}/usr/share/doc/%{name}-%{version}
SUFFIX=gz
mv %{buildroot}/%{_usr}/lib/python%{python_version}/site-packages/bin %{buildroot}/usr/
rm -rf %{buildroot}/%{_usr}/lib/python%{python_version}/site-packages/lib

sed  "s/\/usr\/lib\/python%{python_version}\/site-packages\/bin\/openerp-server/\/usr\/bin\/openerp-server/g" -i files.lst
sed '\/usr\/lib\/python%{python_version}\/site-packages\/lib\//d' -i files.lst
sed "s!\(/share/man/.*\)!\1.$SUFFIX!" -i files.lst
sed "s!\(/usr/share/doc/%{name}-%{version}/.*/.*\)!!" -i files.lst
sed "s!\(/usr/share/doc/%{name}-%{version}/.*\)!!" -i files.lst
sed "s!\(/usr/share/doc/%{name}-%{version}\)!!" -i files.lst

sed "s!\(%{buildroot}\)!!" -i %{buildroot}/%{_bindir}/%{name}-server
find %{buildroot}/%{_usr}/lib/python%{python_version}/site-packages/%{name} -name '*l' -type f -print |xargs chmod -x
find %{buildroot}/%{_usr}/lib/python%{python_version}/site-packages/%{name} -name '*csv' -type f -print |xargs chmod -x
find %{buildroot}/%{_usr}/lib/python%{python_version}/site-packages/%{name} -name '*.py' -type f -print |xargs chmod +x

mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/logrotate.d
mkdir -p %{buildroot}/var/log/openerp
mkdir -p %{buildroot}/var/run/openerp

install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/init.d/%{name}-server
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-server
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}-server.conf


echo "%attr(0775,openerp,openerp) %dir /var/log/openerp" >> files.lst
echo "%attr(0775,openerp,openerp) %dir /var/run/openerp" >> files.lst


%pre

%{GROUPADD_OERP}
%{USERADD_OERP}

%preun
/etc/init.d/%{name} stop

%post

/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 8069 -j ACCEPT 
/sbin/service iptables save

%clean
%__rm -rf %{buildroot};


%files -f files.lst
%doc README README.FIRST
%defattr(-,root,%{OERP_UID_NAME})

%config(noreplace) %{_sysconfdir}/openerp-server.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/openerp-server
%config(noreplace) %{_sysconfdir}/init.d/openerp-server

%changelog
* Tue Nov 04 2013 OpenERP 7.0 RPM <lperez@i-t-m.com> - 7.0
- Agregando archivo de Documentacion despues de la Instalacion
* Tue Oct 31 2013 OpenERP 7.0 RPM <lperez@i-t-m.com> - 7.0
- Agregando Script de Inicializacion y Archivos de Configuracion
* Tue Oct 30 2013 OpenERP 7.0 RPM Build Requires <jandrade@i-t-m.com> - 7.0
- Creacion del RPM de OpenERP 7.0 
* Tue Oct 29 2013 OpenERP 7.0 RPM with Requires <lperez@i-t-m.com> - 7.0
- Creacion del RPM de OpenERP 7.0 
