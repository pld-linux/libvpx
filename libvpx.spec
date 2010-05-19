Summary:	VP8, a high-quality video codec
Name:		libvpx
Version:	0.9.0
Release:	0.1
License:	BSD
Group:		Libraries
Source0:	http://webm.googlecode.com/files/%{name}-%{version}.tar.bz2
# Source0-md5:	9eb8e818d2f3263623c258fe66924082
URL:		http://www.webmproject.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	doxygen
BuildRequires:	php-pcre
BuildRequires:	php-program
BuildRequires:	yasm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
VP8, a high-quality video codec.

%package devel
Summary:	Header files and develpment documentation for libvpx
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description devel
Header files and documentation for libvpx.

%package static
Summary:	Static libvpx library
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
Static libvpx library.

%prep
%setup -q

%build
install -d build
cd build
# not autoconf configure
../configure \
%ifarch %{x8664}
	--target=x86_64-linux-gcc \
%endif
%ifarch %{ix86}
	--target=x86-linux-gcc \
%endif
	--enable-install-docs \
	--enable-vp8 \
	--enable-postproc \
	--enable-runtime-cpu-detect
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/vainfo
%attr(755,root,root) %{_libdir}/libvpx*.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libvpx*.so.1
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/dri
%attr(755,root,root) %{_libdir}/%{name}/dri/*.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvpx*.so
%{_includedir}/va
%{_libdir}/libvpx*.la
%{_pkgconfigdir}/*.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libvpx*.a
