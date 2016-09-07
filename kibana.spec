Name:     kibana
Version:  4.5.4
Release:  2%{?dist}
Summary:  Explore & Visualize Your Data
Group:    Applications/Internet
License:  ASL 2.0
URL:      https://www.elastic.co/products/%{name}
Source0:  https://download.elasticsearch.org/%{name}/%{name}/%{name}-%{version}-linux-x64.tar.gz
Source1:  kibana-sysconfig
Source2:  kibana-logrotate
Source3:  kibana.service
BuildRequires: systemd
Requires: nodejs
Provides: kibana 
%{?systemd_requires}

%description
Explore & Visualize Your Data

%prep
%setup -q -n %{name}-%{version}-linux-x64

%build
true

%install
rm -rf $RPM_BUILD_ROOT

# config #TODO
%{__mkdir} -p %{buildroot}%{_sysconfdir}/kibana
%{__install} -m 644 config/kibana.yml %{buildroot}%{_sysconfdir}/%{name}

# sysconfig
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/kibana

# logs
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/kibana

# systemd
%{__mkdir} -p %{buildroot}%{_unitdir}
%{__install} -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/kibana.service

# sources
%{__mkdir} -p %{buildroot}%{_datadir}/%{name}
%{__cp} -r {bin,config,node_modules,webpackShims,optimize,src,LICENSE.txt,README.txt,package.json} %{buildroot}%{_datadir}/%{name}/

%files
%defattr(-,root,root,-)
%dir %config(noreplace) "/%{_sysconfdir}/sysconfig"
%config(noreplace) "/%{_sysconfdir}/sysconfig/kibana"
%dir %config(noreplace) "/%{_sysconfdir}/kibana"
%config(noreplace) "/%{_sysconfdir}/kibana/kibana.yml"
%config(noreplace) "/%{_sysconfdir}/logrotate.d/kibana"
/%{_unitdir}/kibana.service
%dir %attr(0755, kibana, kibana) "/var/log/kibana"
%ghost "/var/run/kibana.pid"
%doc "/%{_datadir}/kibana/LICENSE.txt"
%doc "/%{_datadir}/kibana/README.txt"
%attr(0644, kibana, kibana) /%{_datadir}/kibana/package.json
%attr(0755, kibana, kibana) /%{_datadir}/kibana/bin
%attr(0755, kibana, kibana) /%{_datadir}/kibana/src
%attr(0755, kibana, kibana) /%{_datadir}/kibana/node_modules
%attr(0755, kibana, kibana) /%{_datadir}/kibana/config
%attr(0755, kibana, kibana) /%{_datadir}/kibana/webpackShims
%attr(0755, kibana, kibana) /%{_datadir}/kibana/optimize


%pre -p /bin/sh
getent group kibana >/dev/null || groupadd -r kibana
getent passwd kibana >/dev/null || \
  useradd -r -g kibana -d /usr/share/kibana -s /sbin/nologin \
  -c "Kibana User" kibana

%post -p /bin/sh
%systemd_post kibana.service
# This should get triggered by the previous line
#[ -f /etc/sysconfig/kibana ] && . /etc/sysconfig/kibana
#/bin/systemctl start kibana.service

%preun
%systemd_preun kibana.service

%postun -p /bin/sh
%systemd_postun_with_restart kibana.service 
# only execute in case of package removal, not on upgrade
if [ $1 -eq 0 ] ; then
  getent passwd kibana > /dev/null
  if [ "$?" == "0" ] ; then
    userdel kibana
  fi

  getent group kibana >/dev/null
  if [ "$?" == "0" ] ; then
    groupdel kibana
  fi
fi

exit


%changelog
* Tue Aug 23 2016 Rich Megginson <rmeggins@redhat.com> - 4.5.4-2
- minor fixes - added package.json

* Thu Aug 18 2016 Rich Megginson <rmeggins@redhat.com> - 4.5.4-1
- new version 4.5.4

* Tue Nov 10 2015 Troy Dawson <tdawson@redhat.com> - 4.1.2-2
- Fixup spec file symlinks

* Tue Oct 6 2015 Chris Murphy <chmurphy@redhat.com> 4.1.2-1
- Bumping to 4.1.2
- Fixing kibana.service file so that it will really start

* Tue Sep 1 2015 Chris Murphy <chmurphy@redhat.com> 4.1.1-1
- Included systemd suggestions from elastic github
- https://github.com/elastic/kibana/pull/3212

* Tue Sep 1 2015 Chris Murphy <chmurphy@redhat.com> 4.1.1-1
- Initial packaging of Kibana 4
