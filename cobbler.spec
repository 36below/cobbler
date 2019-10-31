#
# RPM spec file for all Cobbler packages
#
# Supported/tested build targets:
# - Fedora: 29
# - Fedora: 30
# - CentOS: 7
# - CentOS: 8
#
# If it doesn't build on the Open Build Service (OBS) it's a bug.
# https://build.opensuse.org/project/subprojects/home:libertas-ict
#

%{!?__python3: %global __python3 /usr/bin/python3}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python3_sitearch: %global python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?pyver: %global pyver %(%{__python3} -c "import sys ; print(sys.version[:3])" || echo 0)}

%if 0%{?suse_version}
%define apache_dir /srv/www/
%define apache_etc /etc/apache2/
%define apache_user wwwrun
%define apache_group www
%define apache_log /var/log/apache2/
%define tftp_dir /srv/tftpboot/
%endif

%if 0%{?fedora} || 0%{?rhel}
%define apache_dir /var/www/
%define apache_etc /etc/httpd/
%define apache_user apache
%define apache_group apache
%define apache_log /var/log/httpd/
%define tftp_dir /var/lib/tftpboot/
%endif


#
# Package: cobbler
#

Summary: Boot server configurator
Name: cobbler
License: GPLv2+
Version: 3.0.1
Release: 1%{?dist}
Source0: https://github.com/cobbler/cobbler/releases/cobbler-%{version}.tar.gz
%if 0%{?fedora} || 0%{?rhel}
# Distro specific patch - tftp default location
Patch0:  Set-the-default-tftp_boot-location.patch
%endif
BuildArch: noarch
Url: https://cobbler.github.io

###############################################################################
# Build Requires
###############################################################################

BuildRequires: git
BuildRequires: openssl

# Fedora 29+ and CentOS 8+
%if 0%{?fedora} >= 29 || 0%{?rhel} >= 8
BuildRequires: python3-devel
BuildRequires: python3-cheetah
BuildRequires: %{py3_dist coverage}
BuildRequires: python3-distro
BuildRequires: python3-future
BuildRequires: python3-netaddr
BuildRequires: python3-pyyaml
BuildRequires: python3-requests
BuildRequires: python3-setuptools
BuildRequires: python3-simplejson
BuildRequires: python3-sphinx
%endif

# CentOS 7
# Requires python36 from EPEL and python36-mod_wsgi from IUS
%if 0%{?rhel} == 7
BuildRequires: python36-devel
#BuildRequires: python36-cheetah does not exist
BuildRequires: python36-coverage
BuildRequires: python36-distro
BuildRequires: python36-future
BuildRequires: python36-netaddr
BuildRequires: python36-PyYAML
BuildRequires: python36-requests
BuildRequires: python36-setuptools
BuildRequires: python36-simplejson
BuildRequires: python36-pyflakes
BuildRequires: python36-pycodestyle
BuildRequires: python36-sphinx
%endif

# Common RHEL and Fedora
%if 0%{?fedora} >= 29 || 0%{?rhel} >= 7
BuildRequires: redhat-rpm-config
BuildRequires: systemd-units
%endif

# SUSE
%if 0%{?suse_version} >= 1230
BuildRequires: apache2 >= 2.4
BuildRequires: python3-Cheetah3
BuildRequires: distribution-release
BuildRequires: systemd
BuildRequires: python3-Sphinx
BuildRequires: python3-future
BuildRequires: python3-distro
%endif


###############################################################################
# Requires
###############################################################################

# Common
Requires: python(abi) >= %{pyver}
Requires: createrepo
Requires: rsync
Requires: syslinux >= 4
Requires: logrotate

# CentOS 8+ and Fedora 29+
%if 0%{?fedora} >= 29 || 0%{?rhel} >= 8
Requires: python3 >= 3.6
Requires: python3-distro
Requires: python3-future
Requires: python3-netaddr
Requires: python3-simplejson
Requires: python3-requests
Requires: python3-cheetah
Requires: python3-pyyaml
Requires: python3-tornado
Requires: python3-mod_wsgi
Requires: dnf-plugins-core
%endif

# CentOS 7
%if 0%{?rhel} == 7
Requires: python36 >= 3.6
Requires: python36-distro
Requires: python36-future
Requires: python36-netaddr
Requires: python36-simplejson
Requires: python36-requests
#Requires: python36-cheetah does not exist
Requires: python36-PyYAML
Requires: python36-tornado
Requires: python36-pip
# IUS provides a python36-mod_wsgi package
Requires: python36-mod_wsgi
Requires: yum-utils
%endif

# Common RHEL and Fedora
%if 0%{?fedora} >= 29 || 0%{?rhel} >= 7
Requires: genisoimage
Requires: httpd >= 2.4
Requires: tftp-server
Requires: grub2-efi-ia32-modules
Requires: grub2-efi-x64-modules
Requires(post): systemd-sysv
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif

# SUSE
%if 0%{?suse_version} >= 1230
Requires: python3-PyYAML
Requires: python3-Cheetah3
Requires: apache2 >= 2.4
Requires: apache2-mod_wsgi-python3
Requires: cdrtools
Requires: python3-future
Requires: python3-distro
Requires: python3-tornado
%{?systemd_requires}
Requires: grub2-i386-efi
Requires: grub2-x86_64-efi
Requires(pre): systemd
Requires(post): systemd
Requires(preun): systemd
Requires(preun): systemd
%endif

%description
Cobbler is a PXE and ISO based network install server.
Cobbler's advanced features include importing distributions from DVDs
and rsync mirrors, automatic installation file templating, integrated
package mirroring, and built-in DHCP/DNS Management.

Cobbler has a XMLRPC API for integration with other applications.


%prep
%autosetup -p1


%build
%{__python3} setup.py build


%install
%{__python3} setup.py install --optimize=1 --root=$RPM_BUILD_ROOT $PREFIX

# cobbler
rm $RPM_BUILD_ROOT%{_sysconfdir}/cobbler/cobbler.conf
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mv $RPM_BUILD_ROOT%{_sysconfdir}/cobbler/cobblerd_rotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/cobblerd

mkdir -p $RPM_BUILD_ROOT%{tftp_dir}/images

mkdir -p $RPM_BUILD_ROOT%{_unitdir}
mv $RPM_BUILD_ROOT%{_sysconfdir}/cobbler/cobblerd.service $RPM_BUILD_ROOT%{_unitdir}

# cobbler-web
rm $RPM_BUILD_ROOT%{_sysconfdir}/cobbler/cobbler_web.conf



%pre
# Workaround for missing python36-cheetah package
%if 0%{?rhel} == 7
pip3 install Cheetah3
%endif

if (( $1 >= 2 )); then
    # package upgrade: backup configuration
    DATE=$(date "+%Y%m%d-%H%M%S")
    if [[ ! -d /var/lib/cobbler/backup/upgrade-${DATE} ]]; then
        mkdir -p /var/lib/cobbler/backup/upgrade-${DATE}
    fi
    for i in "config" "snippets" "templates" "triggers" "scripts"; do
        if [[ -d /var/lib/cobbler/${i} ]]; then
            cp -r /var/lib/cobbler/${i} /var/lib/cobbler/backup/upgrade-${DATE}
        fi
    done
    if [[ -d /etc/cobbler ]]; then
        cp -r /etc/cobbler /var/lib/cobbler/backup/upgrade-${DATE}
    fi
fi


%if 0%{?suse_version} >= 1230
%post
# package install
if (( $1 == 1 )); then
    sysconf_addword /etc/sysconfig/apache2 APACHE_MODULES proxy > /dev/null 2>&1
    sysconf_addword /etc/sysconfig/apache2 APACHE_MODULES proxy_http > /dev/null 2>&1
    sysconf_addword /etc/sysconfig/apache2 APACHE_MODULES proxy_connect > /dev/null 2>&1
    sysconf_addword /etc/sysconfig/apache2 APACHE_MODULES rewrite > /dev/null 2>&1
    sysconf_addword /etc/sysconfig/apache2 APACHE_MODULES ssl > /dev/null 2>&1
    sysconf_addword /etc/sysconfig/apache2 APACHE_MODULES wsgi > /dev/null 2>&1
    %service_add_post cobblerd.service
fi
# Create bootloders into /var/lib/cobbler/loaders
%{_prefix}/share/%{name}/bin/mkgrub.sh
%preun
# last package removal
if (( $1 == 0 )); then
    %service_del_preun cobblerd.service
fi
%postun
# last package removal
if (( $1 == 0 )); then
    %service_del_postun cobblerd.service
fi
if [ -e /var/lib/cobbler/loaders/.cobbler_postun_cleanup ];then
    for file in $(cat /var/lib/cobbler/loaders/.cobbler_postun_cleanup);do
        rm /var/lib/cobbler/loaders/$file
    done
    rm -rf /var/lib/cobbler/loaders/.cobbler_postun_cleanup
fi
%endif


%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%post
# package install
if (( $1 == 1 )); then
    echo "Enabling cobblerd..."
    /usr/bin/systemctl enable cobblerd.service > /dev/null 2>&1
    echo "Starting cobblerd..."
    /usr/bin/systemctl start cobblerd.service > /dev/null 2>&1
    echo "Restarting httpd..."
    /usr/bin/systemctl restart httpd.service > /dev/null 2>&1
fi
%preun
# last package removal
if (( $1 == 0 )); then
    echo "Disabling cobblerd..."
    /usr/bin/systemctl disable cobblerd.service > /dev/null 2>&1
    echo "Stopping cobblerd..."
    /usr/bin/systemctl stop cobblerd.service > /dev/null 2>&1
fi
%postun
# last package removal
if (( $1 == 0 )); then
    echo "Restarting httpd..."
    /usr/bin/systemctl try-restart httpd.service > /dev/null 2>&1
fi
%endif


%files
# binaries
%{_bindir}/cobbler
%{_bindir}/cobbler-ext-nodes
%{_bindir}/cobblerd
%{_sbindir}/tftpd.py

# python
%{python3_sitelib}/cobbler/*.py*
%{python3_sitelib}/cobbler/__pycache__/*.py*
%{python3_sitelib}/cobbler/actions/*.py*
%{python3_sitelib}/cobbler/actions/__pycache__/*.py*
%{python3_sitelib}/cobbler/cobbler_collections/*.py*
%{python3_sitelib}/cobbler/cobbler_collections/__pycache__/*.py*
%{python3_sitelib}/cobbler/items/*.py*
%{python3_sitelib}/cobbler/items/__pycache__/*.py*
%{python3_sitelib}/cobbler/modules/*.py*
%{python3_sitelib}/cobbler/modules/__pycache__/*.py*
%{python3_sitelib}/cobbler/modules/authentication/*.py*
%{python3_sitelib}/cobbler/modules/authentication/__pycache__/*.py*
%{python3_sitelib}/cobbler/modules/authorization/*.py*
%{python3_sitelib}/cobbler/modules/authorization/__pycache__/*.py*
%{python3_sitelib}/cobbler/modules/installation/*.py*
%{python3_sitelib}/cobbler/modules/installation/__pycache__/*.py*
%{python3_sitelib}/cobbler/modules/managers/*.py*
%{python3_sitelib}/cobbler/modules/managers/__pycache__/*.py*
%{python3_sitelib}/cobbler/modules/serializers/*.py*
%{python3_sitelib}/cobbler/modules/serializers/__pycache__/*.py*
%{python3_sitelib}/cobbler*.egg-info
%exclude %{python3_sitelib}/cobbler/modules/nsupdate*
%exclude %{python3_sitelib}/cobbler/web


# configuration
%config(noreplace) %{_sysconfdir}/cobbler
%exclude %{_sysconfdir}/cobbler/settings.d/nsupdate.settings

%config(noreplace) %{_sysconfdir}/logrotate.d/cobblerd
%dir %{apache_etc}
%if 0%{?suse_version} >= 1230
%dir %{apache_etc}/vhosts.d
%config(noreplace) %{apache_etc}/vhosts.d/cobbler.conf
%else
%dir %{apache_etc}/conf.d
%config(noreplace) %{apache_etc}/conf.d/cobbler.conf
%endif

%{_unitdir}/cobblerd.service

# data
%{tftp_dir}
%{apache_dir}/cobbler
%{_var}/lib/cobbler
%exclude %{apache_dir}/cobbler_webui_content
%exclude %{_var}/lib/cobbler/webui_sessions

# share
%{_usr}/share/cobbler
#%exclude %{_usr}/share/cobbler/spool
%exclude %{_usr}/share/cobbler/web

# log
%{_var}/log/cobbler

# documentation
%doc AUTHORS COPYING README
%{_mandir}/man1/cobblerd.1.gz
%{_mandir}/man1/cobbler-cli.1.gz
%{_mandir}/man1/cobbler.conf.5.gz


#
# package: cobbler-web
#

%package -n cobbler-web

Summary: Web interface for Cobbler
Requires: python(abi) >= %{pyver}
Requires: cobbler
Requires(post): openssl


%if 0%{?fedora} || 0%{?rhel}
Requires: httpd >= 2.4
%endif

%if 0%{?fedora} >= 29 || 0%{?rhel} >= 8
Requires: python3-mod_wsgi
Requires: python3-django >= 1.8
%endif

%if 0%{?rhel} == 7
# IUS provides a python36-mod_wsgi package
Requires: python36-mod_wsgi
Requires: python36-django >= 1.8
%endif


%if 0%{?suse_version} >= 1230
Requires: apache2 >= 2.4
Requires: apache2-mod_wsgi-python3
Requires: python3-Django >= 1.7
%endif


%description -n cobbler-web
Web interface for Cobbler that allows visiting
http://server/cobbler_web to configure the install server.


%post -n cobbler-web
# Change the SECRET_KEY option in the Django settings.py file
# required for security reasons, should be unique on all systems
RAND_SECRET=$(openssl rand -base64 40 | sed 's/\//\\\//g')
sed -i -e "s/SECRET_KEY = ''/SECRET_KEY = \'$RAND_SECRET\'/" /usr/share/cobbler/web/settings.py


%files -n cobbler-web
%doc AUTHORS COPYING README

%{python3_sitelib}/cobbler/web/
%exclude %{python3_sitelib}/cobbler/web/settings.py
%exclude %{python3_sitelib}/cobbler/web/__pycache__

%dir %{apache_etc}
%if 0%{?suse_version} >= 1230
%dir %{apache_etc}/vhosts.d
%config(noreplace) %{apache_etc}/vhosts.d/cobbler_web.conf
%else
%dir %{apache_etc}/conf.d
%config(noreplace) %{apache_etc}/conf.d/cobbler_web.conf
%endif

%{apache_dir}/cobbler_webui_content/

%if 0%{?fedora} >=18 || 0%{?rhel} >= 7
%defattr(-,apache,apache,-)
/usr/share/cobbler/web
%dir %attr(700,apache,root) %{_var}/lib/cobbler/webui_sessions
%endif

%if 0%{?suse_version} >= 1230
%defattr(-,%{apache_user},%{apache_group},-)
/usr/share/cobbler/web
%dir %attr(700,%{apache_user},%{apache_group}) %{_var}/lib/cobbler/webui_sessions
%endif

#
# package: cobbler-nsupdate
#

%package -n cobbler-nsupdate

Summary: module for dynamic dns updates
Requires: cobbler

%if 0%{?fedora} >= 29 || 0%{?rhel} >= 8
Requires: python3-dns
%endif

%if 0%{?rhel} == 7
Requires: python36-dns
%endif

%description -n cobbler-nsupdate
Cobbler module providing secure dynamic dns updates

%files -n cobbler-nsupdate
%config(noreplace) %{_sysconfdir}/cobbler/settings.d/nsupdate.settings
%{python3_sitelib}/cobbler/modules/nsupdate*

%doc AUTHORS COPYING README


%changelog
* Fri Jul 18 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.6.3 release
- Cobbler 2.4.6 release
* Tue Jul 15 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.6.2 release
* Sun Jul 13 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.4.5 release
* Thu May 22 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.6.1 release
* Tue Apr 22 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.4.4 release
* Sun Apr 13 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.6.0 release
* Wed Mar 19 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.4.3 release
* Sat Feb 15 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.4.2 release
* Mon Feb 03 2014 Jörgen Maas <jorgen.maas@gmail.com>
- Cobbler 2.4.1 release
* Thu Jun 20 2013 James Cammarata <jimi@sngx.net>
- Cobbler 2.4.0-1 release
* Sun Jun 17 2012 James Cammarata <jimi@sngx.net>
- Cobbler 2.2.3-2 release
* Tue Jun 05 2012 James Cammarata <jimi@sngx.net>
- Cobbler 2.2.3-1 release
* Tue Nov 15 2011 Scott Henson <shenson@redhat.com>
- Cobbler 2.2.2-1 release
* Wed Oct 05 2011 Scott Henson <shenson@redhat.com>
- Cobbler 2.2.1-1 release
* Wed Oct 05 2011 Scott Henson <shenson@redhat.com>
- Cobbler 2.2.0-1 release
* Tue Apr 27 2010 Scott Henson <shenson@redhat.com>
- Cobbler 2.0.4-1 release
* Thu Apr 15 2010 Devan Goodwin <dgoodwin@rm-rf.ca>
- Cobbler 2.0.3.2-1 release
* Mon Mar  1 2010 Scott Henson <shenson@redhat.com>
- Cobbler 2.0.3.1-3 release
* Mon Mar  1 2010 Scott Henson <shenson@redhat.com>
- Cobbler 2.0.3.1-2 release
* Mon Feb 15 2010 Scott Henson <shenson@redhat.com>
- Cobbler 2.0.3.1-1 release
* Thu Feb 11 2010 Scott Henson <shenson@redhat.com>
- Cobbler 2.0.3-1 release
* Mon Nov 23 2009 John Eckersberg <jeckersb@redhat.com>
- Cobbler 2.0.2-1 release
* Tue Sep 15 2009 Michael DeHaan <michael.dehaan AT gmail>
- Cobbler 2.0.0-1 release

# EOF
