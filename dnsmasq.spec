# TODO:
# - subpackage DNSmasq webmin module (contrib/webmin)
#
# Conditional build:
%bcond_without	dbus		# DBus interface
%bcond_without	idn		# IDN via libidn2
%bcond_without	conntrack	# conntrack support
%bcond_without	nftables	# nftables support
%bcond_with	lua		# Lua support

Summary:	A lightweight caching server (DNS, DHCP)
Summary(pl.UTF-8):	Lekki buforujący serwer nazw (DNS) i DHCP
Name:		dnsmasq
Version:	2.91
Release:	2
License:	GPL v2
Group:		Networking/Daemons
# TODO:	http://thekelleys.org.uk/dnsmasq/%{name}-%{version}.tar.xz
Source0:	https://thekelleys.org.uk/dnsmasq/%{name}-%{version}.tar.gz
# Source0-md5:	66e227a971ec29299f18274251440571
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.service
URL:		http://www.thekelleys.org.uk/dnsmasq/doc.html
%{?with_dbus:BuildRequires:	dbus-devel}
BuildRequires:	gettext-tools
BuildRequires:	gmp-devel
%{?with_idn:BuildRequires:	libidn2-devel}
%{?with_conntrack:BuildRequires:	libnetfilter_conntrack-devel}
%{?with_lua:BuildRequires:	lua52-devel}
BuildRequires:	nettle-devel
%{?with_nftables:BuildRequires:	nftables-devel}
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.671
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 38
Requires:	rc-scripts
Provides:	caching-nameserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		copts	-DHAVE_DNSSEC%{?with_dbus: -DHAVE_DBUS}%{?with_idn: -DHAVE_LIBIDN2}%{?with_conntrack: -DHAVE_CONNTRACK}%{?with_lua: -DHAVE_LUASCRIPT}%{?with_nftables: -DHAVE_NFTSET}

%description
Dnsmasq is a lightweight, easy to configure DNS forwarder and DHCP
server. It is designed to provide DNS and, optionally, DHCP, to a
small network. It can serve the names of local machines which are not
in the global DNS. The DHCP server integrates with the DNS server and
allows machines with DHCP-allocated addresses to appear in the DNS
with names configured either in each host or in a central
configuration file. Dnsmasq supports static and dynamic DHCP leases
and BOOTP for network booting of diskless machines.

Dnsmasq is targeted at home networks using NAT and connected to the
Internet via a modem, cable-modem or ADSL connection but would be a
good choice for any small network where low resource use and ease of
configuration are important.

%description -l pl.UTF-8
dnsmasq jest lekkim, łatwym w konfiguracji forwarderem DNS i serwerem
DHCP zaprojektowanym do serwowania usługi DNS i opcjonalnie DHCP dla
małych sieci. Może on serwować także nazwy dla lokalnych maszyn nie
znajdujących się w globalnym DNS-ie. Serwer DHCP integruje się z
serwerem DNS, umożliwiając maszynom o adresach przydzielonych przez
DHCP pojawienie się w DNS-ie z nazwami konfigurowanymi dla każdego
hosta lub w centralnym pliku konfiguracyjnym. dnsmasq obsługuje
statyczne i dynamiczne dzierżawy DHCP oraz BOOTP do uruchamiania z
sieci maszyn bezdyskowych.

dnsmasq jest przeznaczony głównie dla sieci domowych używających NAT-u
i podłączonych do Internetu przez modem, modem kablowy lub łącze ADSL,
ale jest dobrym wyborem dla dowolnej małej sieci, gdzie ważne jest
małe wykorzystanie zasobów i łatwa konfiguracja.

%prep
%setup -q

%build
%{__make} all-i18n \
	CC="%{__cc}" \
	CFLAGS="%{rpmcppflags} %{rpmcflags} -DHAVE_ISC_READER" \
	LDFLAGS="%{rpmldflags}" \
	COPTS="%{copts}" \
	PREFIX=%{_prefix}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/dbus-1/system.d,/etc/sysconfig,/etc/rc.d/init.d} \
	$RPM_BUILD_ROOT{%{systemdunitdir},%{_mandir}/man8,%{_datadir}/dnsmasq}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dnsmasq
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/dnsmasq
install dnsmasq.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.conf

install contrib/port-forward/dnsmasq-portforward $RPM_BUILD_ROOT%{_sbindir}
install contrib/port-forward/portforward $RPM_BUILD_ROOT%{_sysconfdir}

install %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}/dnsmasq.service

install -p trust-anchors.conf $RPM_BUILD_ROOT%{_datadir}/dnsmasq

%{__make} install-i18n \
	CC="%{__cc}" \
	CFLAGS="%{rpmcppflags} %{rpmcflags} -DHAVE_ISC_READER" \
	LDFLAGS="%{rpmldflags}" \
	COPTS="%{copts}" \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix}

%{__mv} $RPM_BUILD_ROOT%{_datadir}/locale/{no,nb}

%if %{with dbus}
cp -p dbus/dnsmasq.conf $RPM_BUILD_ROOT/etc/dbus-1/system.d/dnsmasq.conf
%endif

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add dnsmasq
%service dnsmasq restart
%systemd_post dnsmasq.service

%preun
if [ "$1" = "0" ]; then
	%service dnsmasq stop
	/sbin/chkconfig --del dnsmasq
fi
%systemd_preun dnsmasq.service

%postun
%systemd_reload

%triggerpostun -- dnsmasq < 2.68-1.1
if [ -f /etc/sysconfig/dnsmasq ]; then
	__OPT=
	. /etc/sysconfig/dnsmasq
	[ -n "$MAILHOSTNAME" ] &&  __OPT="-m $MAILHOSTNAME"
	[ -n "$RESOLV_CONF" ] && __OPT="$__OPT -r $RESOLV_CONF"
	[ -n "$DHCP_LEASE" ] && __OPT="$__OPT -l $DHCP_LEASE"
	[ -n "$DOMAIN_SUFFIX" ] && __OPT="$__OPT -s $DOMAIN_SUFFIX"
	[ -n "$INTERFACE" ] && __OPT="$__OPT -i $INTERFACE"
	if [ -n "$__OPT" ]; then
		%{__cp} -f /etc/sysconfig/dnsmasq{,.rpmsave}
		echo >>/etc/sysconfig/dnsmasq
		echo "# Added by rpm trigger" >>/etc/sysconfig/dnsmasq
		echo "OPTIONS=\"$OPTIONS $__OPT\"" >>/etc/sysconfig/dnsmasq
	fi
fi
%systemd_trigger dnsmasq.service

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc CHANGELOG FAQ *.html contrib/{dnslist,dynamic-dnsmasq}
%{?with_dbus:%config(noreplace) %verify(not md5 mtime size) /etc/dbus-1/system.d/dnsmasq.conf}
%attr(754,root,root) /etc/rc.d/init.d/dnsmasq
%{systemdunitdir}/dnsmasq.service
%attr(755,root,root) %{_sbindir}/dnsmasq
%attr(755,root,root) %{_sbindir}/dnsmasq-portforward
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/dnsmasq
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dnsmasq.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/portforward
%{_mandir}/man8/dnsmasq.8*
%lang(es) %{_mandir}/es/man8/dnsmasq.8*
%lang(fr) %{_mandir}/fr/man8/dnsmasq.8*
%dir %{_datadir}/dnsmasq
%{_datadir}/dnsmasq/trust-anchors.conf
