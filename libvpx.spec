#
# Conditional build:
%bcond_without	asm	# x86 assembler
%bcond_without	doc	# don't build doc
%bcond_without	tests	# build without tests
%bcond_without	ssse3	# use SSSE3 instructions (Intel since Core2, Via Nano)

%ifnarch %{ix86} %{x8664}
%undefine	with_asm
%endif

%if "%{pld_release}" == "ac"
# not supported by compiler
%undefine	with_ssse3
%endif

Summary:	VP8, a high-quality video codec
Summary(pl.UTF-8):	VP8 - kodek obrazu wysokiej jakości
Name:		libvpx
Version:	1.3.0
Release:	1
License:	BSD
Group:		Libraries
#Source0Download: http://code.google.com/p/webm/downloads/list
#Source0:	https://webm.googlecode.com/files/%{name}-v%{version}.tar.bz2
# source, but regenerated on each fetch
#Source0:	https://chromium.googlesource.com/webm/libvpx/+archive/v%{version}.tar.gz?/%{name}-%{version}.tar.gz
Source0:	%{name}-%{version}.tar.gz
# Source0-md5:	dcf436a5dc8b56bdfb4aec63b2fe6729
URL:		http://www.webmproject.org/
BuildRequires:	doxygen
BuildRequires:	rpmbuild(macros) >= 1.673
BuildRequires:	sed >= 4.0
%{?with_asm:BuildRequires:	yasm >= 0.8}
%if %{with doc}
BuildRequires:	%{php_name}-pcre
BuildRequires:	%{php_name}-program
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	generic_target	generic-gnu
%define	vpxtarget	%{generic_target}
%ifarch %{x8664}
%define	vpxtarget	x86_64-linux-gcc
%endif
%ifarch %{ix86}
%define	vpxtarget	x86-linux-gcc
%endif
%ifarch ppc
%define	vpxtarget	ppc32-linux-gcc
%endif
%ifarch ppc64
%define	vpxtarget	ppc64-linux-gcc
%endif

%description
VP8, a high-quality video codec.

%description -l pl.UTF-8
VP8 - kodek obrazu wysokiej jakości.

%package devel
Summary:	Header files for libvpx
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libvpx
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for libvpx library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libvpx.

%package static
Summary:	Static libvpx library
Summary(pl.UTF-8):	Statyczna biblioteka libvpx
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libvpx library.

%description static -l pl.UTF-8
Statyczna biblioteka libvpx.

%prep
#%setup -q -n %{name}-v%{version}
%setup -qc

%build
install -d obj
cd obj
# not autoconf configure
CFLAGS="%{rpmcflags} %{rpmcppflags}" \
../configure \
%if %{with asm}
	--as=yasm \
%endif
	--target=%{vpxtarget} \
%if "%{vpxtarget}" != "%{generic_target}"
	--enable-shared \
%endif
	%{!?with_ssse3:--disable-ssse3} \
	--disable-optimizations \
	--%{!?with_tests:dis}%{?with_tests:en}able-unit-tests \
	--enable-vp8 \
	--enable-postproc \
	--enable-runtime-cpu-detect

%{__make} verbose=true target=libs \
	HAVE_GNU_STRIP=no \
	CC="%{__cc}" \
	LD="%{__cc}" \
	LDFLAGS="%{rpmldflags}"

%{__make} verbose=true target=examples \
	CC="%{__cc}" \
	LD="%{__cc}" \
	LDFLAGS="%{rpmldflags} -L."

%if %{with doc}
%{__make} verbose=true target=docs
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/vpx,%{_libdir}}

%{__make} -C obj verbose=true install \
	LIBSUBDIR=%{_lib} \
	DIST_DIR=$RPM_BUILD_ROOT%{_prefix}

%{__rm} $RPM_BUILD_ROOT%{_libdir}/libvpx.so.1.3

# adjust prefix and libdir
%{__sed} -i -e 's,^prefix=.*,prefix=%{_prefix},;s,^libdir=.*,libdir=%{_libdir},' $RPM_BUILD_ROOT%{_pkgconfigdir}/vpx.pc

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG LICENSE PATENTS README
%attr(755,root,root) %{_bindir}/vp8_scalable_patterns
%attr(755,root,root) %{_bindir}/vp9_spatial_scalable_encoder
%attr(755,root,root) %{_bindir}/vpxdec
%attr(755,root,root) %{_bindir}/vpxenc
%attr(755,root,root) %{_libdir}/libvpx.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvpx.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvpx.so
%{_includedir}/vpx
%{_pkgconfigdir}/vpx.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libvpx.a
