Summary:	A lightweight caching server (DNS, DHCP)
Summary(pl):	Lekki buforuj±cy serwer nazw (DNS, DHCP)
Name:		dnsmasq
Version:	2.35
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://thekelleys.org.uk/dnsmasq/%{name}-%{version}.tar.gz
# Source0-md5:	57b8643dc394cf2fbd1bced64536c6df
Source1:	%{name}.init
Source2:	%{name}.config
URL:		http://www.thekelleys.org.uk/dnsmasq/doc.html
BuildRequires:	gettext-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
Provides:	caching-nameserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Dnsmasq is a lightweight, easy to configure DNS forwarder and DHCP server.
It is designed to provide DNS and, optionally, DHCP, to a small network. It
can serve the names of local machines which are not in the global DNS. The
DHCP server integrates with the DNS server and allows machines with
DHCP-allocated addresses to appear in the DNS with names configured either
in each host or in a central configuration file. Dnsmasq supports static and
dynamic DHCP leases and BOOTP for network booting of diskless machines.

Dnsmasq is targeted at home networks using NAT and connected to the internet
via a modem, cable-modem or ADSL connection but would be a good choice for
any small network where low resource use and ease of configuration are
important. 

%description -l pl
Dnsmasq jest lekkim, ³atwym w konfiguracji forwarderem DNS
zaprojektowanym do serwowania us³ugi DNS dla ma³ych sieci, gdzie
u¿ywanie BIND by³oby przesad±. Zewnêtrzne serwery DNS mog± byæ
automatycznie konfigurowane przez PPP lub DHCP. Mo¿e on serwowaæ tak¿e
nazwy dla lokalnych maszyn nie znajduj±cych siê w globalnym DNS. Jest
idealny dla sieci za NAT i po³±czonych przez modem, ISDL, ADSL lub
po³±czenia kablowe.

%prep
%setup -q

%build
%{__make} all-i18n \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -DHAVE_ISC_READER" \
	PREFIX=%{_prefix}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/sysconfig,/etc/rc.d/init.d,%{_mandir}/man8}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dnsmasq
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/dnsmasq
install dnsmasq.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.conf

%{__make} install-i18n \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix}

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add dnsmasq
%service dnsmasq restart

%preun
if [ "$1" = "0" ]; then
	%service dnsmasq stop
	/sbin/chkconfig --del dnsmasq
fi

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc CHANGELOG FAQ *.html contrib/{dnslist,dynamic-dnsmasq,port-forward}
%attr(754,root,root) /etc/rc.d/init.d/dnsmasq
%attr(755,root,root) %{_sbindir}/dnsmasq
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/dnsmasq
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dnsmasq.conf
%{_mandir}/man8/*
%lang(es) %{_mandir}/es/man8/* 
