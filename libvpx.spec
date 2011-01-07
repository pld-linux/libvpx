#
# Conditional build:
%bcond_without	asm	# x86 assembler
#
Summary:	VP8, a high-quality video codec
Summary(pl.UTF-8):	VP8 - kodek obrazu wysokiej jakości
Name:		libvpx
Version:	0.9.5
Release:	2
License:	BSD
Group:		Libraries
#Source0-Download: http://code.google.com/p/webm/downloads/list
Source0:	http://webm.googlecode.com/files/%{name}-v%{version}.tar.bz2
# Source0-md5:	4bf2f2c76700202c1fe9201fcb0680e3
Source1:	%{name}.ver
Patch0:		%{name}-0.9.0-no-explicit-dep-on-static-lib.patch
URL:		http://www.webmproject.org/
BuildRequires:	/usr/bin/php
BuildRequires:	doxygen
BuildRequires:	php-common >= 4:5.0.0
BuildRequires:	php-pcre
%ifarch %{ix86} %{x8664}
%{?with_asm:BuildRequires:	yasm}
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
%setup -q -n %{name}-v%{version}
%patch0 -p1

%build
install -d obj
cd obj
# not autoconf configure
CFLAGS="%{rpmcflags} %{rpmcppflags}" \
../configure \
%if %{with asm}
%ifarch %{x8664}
	--target=x86_64-linux-gcc \
%endif
%ifarch %{ix86}
	--target=x86-linux-gcc \
%endif
%else
	--target=generic-gnu \
%endif
	--enable-shared \
	--disable-optimizations \
	--enable-vp8 \
	--enable-postproc \
	--enable-runtime-cpu-detect

# disable stripping
sed -i "s|STRIP=.*|STRIP=|g" {libs,examples,docs}-*.mk

%{__make} verbose=true target=libs \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}"

%{__make} verbose=true target=examples \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}"
%{__make} verbose=true target=docs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/vpx,%{_libdir}}

install -d outdir
%{__make} -C obj verbose=true install \
	DIST_DIR=$(pwd)/outdir

install -p outdir/bin/* $RPM_BUILD_ROOT%{_bindir}
install -p obj/libvpx.so.* $RPM_BUILD_ROOT%{_libdir}
ln -s libvpx.so.0.9.5 $RPM_BUILD_ROOT%{_libdir}/libvpx.so.0
ln -s libvpx.so.0.9.5 $RPM_BUILD_ROOT%{_libdir}/libvpx.so

cp -a outdir/include/vpx/*.h $RPM_BUILD_ROOT%{_includedir}/vpx
cp -a outdir/lib/*.a $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG LICENSE PATENTS README
%attr(755,root,root) %{_bindir}/vpxdec
%attr(755,root,root) %{_bindir}/vpxenc
%attr(755,root,root) %{_libdir}/libvpx.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvpx.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvpx.so
%{_includedir}/vpx

%files static
%defattr(644,root,root,755)
%{_libdir}/libvpx.a
