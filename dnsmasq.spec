Summary:	A lightweight caching nameserver
Summary(pl):	Lekki buforuj±cy serwer nazw (DNS)
Name:		dnsmasq
Version:	1.11
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	http://thekelleys.org.uk/dnsmasq/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.config
Patch0:		%{name}-cc.patch
URL:		http://www.thekelleys.org.uk/dnsmasq/
PreReq:		/sbin/chkconfig
Provides:	caching-nameserver
Obsoletes:	caching-nameserver
Obsoletes:	nameserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Dnsmasq is lightweight, easy to configure DNS forwarder designed to
provide DNS (domain name) services to a small network where using BIND
would be overkill. It can be have its DNS servers automatically
configured by PPP or DHCP, and it can serve the names of local
machines which are not in the global DNS. It is ideal for networks
behind NAT routers and connected via modem, ISDN, ADSL, or cable-modem
connections.

%description -l pl
Dnsmasq jest lekkim, ³atwym do konfiguracji forwarderem DNS
zaprojektowanym do serwowania us³ugi DNS dla ma³ych sieci, gdzie u¿ywanie
BIND by³o by przesad±. Zewnêtrzne serwery DNS mog± byæ automatycznie
konfigurowane przez PPP lub DHCP. Mo¿e on serwowaæ tak¿e nazwy dla lokalnych
maszyn nie znajduj±cych siê w globalnym DNS. Jest idealny dla sieci za NAT
i po³±czonych przez modem, ISDL, ADSL lub po³±czenia kablowe.

%prep
%setup -q
%patch0 -p1

%build
%{__make} CC=%{__cc} OPT="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/sysconfig,/etc/rc.d/init.d,%{_mandir}/man8}

install %SOURCE1 $RPM_BUILD_ROOT/etc/rc.d/init.d/dnsmasq
install %SOURCE2 $RPM_BUILD_ROOT/etc/sysconfig/dnsmasq
install dnsmasq $RPM_BUILD_ROOT%{_sbindir}
install dnsmasq.8 $RPM_BUILD_ROOT%{_mandir}/man8

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add dnsmasq
if [ -f %{_localstatedir}/lock/subsys/dnsmasq ]; then
	/etc/rc.d/init.d/dnsmasq restart >&2
else
	echo "Run \"/etc/rc.d/init.d/dnsmasq start\" to start dnsmasq." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f %{_localstatedir}/lock/subsys/dnsmasq ]; then
		/etc/rc.d/init.d/dnsmasq stop
	fi
	/sbin/chkconfig --del dnsmasq
fi

%files
%defattr(644,root,root,755)
%doc CHANGELOG FAQ *.html
%attr(755,root,root) /etc/rc.d/init.d/dnsmasq
%attr(755,root,root) %{_sbindir}/dnsmasq
%config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/dnsmasq
%{_mandir}/man8/*
