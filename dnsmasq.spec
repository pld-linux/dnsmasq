# TODO:
# - subpackage DNSmasq webmin module (contrib/webmin)
#
Summary:	A lightweight caching server (DNS, DHCP)
Summary(pl.UTF-8):	Lekki buforujący serwer nazw (DNS) i DHCP
Name:		dnsmasq
Version:	2.41
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://thekelleys.org.uk/dnsmasq/%{name}-%{version}.tar.gz
# Source0-md5:	b067598c3e9b91819a8be5cb59cbf90e
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
Dnsmasq is a lightweight, easy to configure DNS forwarder and DHCP
server.  It is designed to provide DNS and, optionally, DHCP, to a
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
	CFLAGS="%{rpmcflags} -DHAVE_ISC_READER" \
	PREFIX=%{_prefix}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/sysconfig,/etc/rc.d/init.d,%{_mandir}/man8}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dnsmasq
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/dnsmasq
install dnsmasq.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.conf

install contrib/port-forward/dnsmasq-portforward $RPM_BUILD_ROOT%{_sbindir}
install contrib/port-forward/portforward $RPM_BUILD_ROOT%{_sysconfdir}

%{__make} install-i18n \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix}

mv -f $RPM_BUILD_ROOT%{_datadir}/locale/{no,nb}

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
%doc CHANGELOG FAQ *.html contrib/{dnslist,dynamic-dnsmasq}
%attr(754,root,root) /etc/rc.d/init.d/dnsmasq
%attr(755,root,root) %{_sbindir}/dnsmasq*
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/dnsmasq
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dnsmasq.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/portforward
%{_mandir}/man8/*
%lang(es) %{_mandir}/es/man8/* 
