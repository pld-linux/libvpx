#
# Conditional build:
%bcond_without	asm		# x86 assembler
%bcond_without	doc		# don't build doc
%bcond_with	tests		# build tests (not useful, creates libgtest.a)
%bcond_without	ssse3		# use SSSE3 instructions (Intel since Core2, Via Nano)
%bcond_without	static_libs	# static library

%ifnarch %{ix86} %{x8664} x32
%undefine	with_asm
%endif

%if "%{pld_release}" == "ac"
# not supported by compiler
%undefine	with_ssse3
%endif

Summary:	VP8, a high-quality video codec
Summary(pl.UTF-8):	VP8 - kodek obrazu wysokiej jakości
Name:		libvpx
Version:	1.14.0
Release:	1
License:	BSD
Group:		Libraries
# original download URL: http://downloads.webmproject.org/releases/webm/index.html
# ...but use github mirror to get consistent tarballs
#Source0Download: https://github.com/webmproject/libvpx/tags
Source0:	https://github.com/webmproject/libvpx/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	026bc289d916624dabdfd713c1c5b69a
URL:		https://www.webmproject.org/
BuildRequires:	doxygen
BuildRequires:	libstdc++-devel
BuildRequires:	perl-base
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.673
BuildRequires:	sed >= 4.0
%{?with_asm:BuildRequires:	yasm >= 0.8}
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
%ifarch aarch64
%define	vpxtarget	arm64-linux-gcc
%endif
%ifarch armv7hnl
%define	vpxtarget	armv7-linux-gcc
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

%package tools
Summary:	VPX decoding/encoding tools
Summary(pl.UTF-8):	Narzędzia do kodowania/dekodowania formatu VPX
Group:		Applications/Graphics
Requires:	%{name} = %{version}-%{release}

%description tools
VPX decoding/encoding tools.

%description tools -l pl.UTF-8
Narzędzia do kodowania/dekodowania formatu VPX.

%prep
%setup -q

%build
install -d obj
cd obj
# not autoconf configure
CC="%{__cc}" \
CXX="%{__cxx}" \
CFLAGS="%{rpmcflags} %{rpmcppflags}" \
../configure \
%if %{with asm}
	--as=yasm \
%endif
	--target=%{vpxtarget} \
	--enable-shared \
	%{!?with_static_libs:--disable-static} \
	%{!?with_ssse3:--disable-ssse3} \
	--disable-optimizations \
	--%{!?with_tests:dis}%{?with_tests:en}able-unit-tests \
	--%{!?with_doc:dis}%{?with_doc:en}able-docs \
	--%{!?with_doc:dis}%{?with_doc:en}able-install-docs \
	--enable-vp8 \
	--enable-vp8 \
	--enable-postproc \
	--enable-runtime-cpu-detect

%{__make} verbose=true target=libs \
	HAVE_GNU_STRIP=no \
	LDFLAGS="%{rpmldflags}"

%{__make} verbose=true target=examples \
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

# redundant minor version symlink (not SONAME)
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libvpx.so.9.0

# adjust prefix and libdir
%{__sed} -i -e 's,^prefix=.*,prefix=%{_prefix},;s,^libdir=.*,libdir=%{_libdir},' $RPM_BUILD_ROOT%{_pkgconfigdir}/vpx.pc

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG LICENSE PATENTS README
%attr(755,root,root) %{_libdir}/libvpx.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvpx.so.9

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvpx.so
%{_includedir}/vpx
%{_pkgconfigdir}/vpx.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libvpx.a
%endif

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/vpxdec
%attr(755,root,root) %{_bindir}/vpxenc
