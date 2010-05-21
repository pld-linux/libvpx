#
# Conditional build:
%bcond_without	asm

%ifarch %{x8664}
# buggy, non PIC asm code
%undefine with_asm
%endif

Summary:	VP8, a high-quality video codec
Name:		libvpx
Version:	0.9.0
Release:	2
License:	BSD
Group:		Libraries
Source0:	http://webm.googlecode.com/files/%{name}-%{version}.tar.bz2
# Source0-md5:	9eb8e818d2f3263623c258fe66924082
Patch0:		%{name}-0.9.0-no-explicit-dep-on-static-lib.patch
URL:		http://www.webmproject.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	doxygen
%{?with_asm:BuildRequires:	yasm}
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
%patch0 -p1

%build
install -d build
cd build
# not autoconf configure
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
	--enable-pic \
	--disable-optimizations \
	--enable-vp8 \
	--enable-postproc \
	--enable-runtime-cpu-detect

# Hack our optflags in.
sed -i "s|\"vpx_config.h\"|\"vpx_config.h\" %{rpmcflags} %{rpmcppflags} -fPIC|g" {libs,examples,docs}-*.mk
sed -i "s|STRIP=.*|STRIP=|g" {libs,examples,docs}-*.mk

%{__make} verbose=true target=libs \
	CC="%{__cc}"

%{__cc} %{rpmldflags} -fPIC -o libvpx.so.0.0.0 -shared -Wl,-soname,libvpx.so.0 vpx_codec/src/*.o vpx_mem/*.o \
	vpx_scale/generic/*.o vp8/common/*.o vp8/common/generic/*.o vp8/*.o vp8/encoder/*.o \
	vp8/encoder/generic/*.o vp8/decoder/*.o vp8/decoder/generic/*.o vpx_config.c.o \
%if %{with asm}
	vp8/common/x*/*.o vp8/encoder/x*/*.o vp8/decoder/x*/*.o vpx_ports/*.o \
%endif
	-lm -lpthread

# Temporarily dance the static libs out of the way
mv libvpx.a libNOTvpx.a
mv libvpx_g.a libNOTvpx_g.a

# We need to do this so the examples can link against it.
ln -sf libvpx.so.0.0.0 libvpx.so

%{__make} verbose=true target=examples \
	CC="%{__cc}"
%{__make} verbose=true target=docs

# Put them back so the install doesn't fail
mv libNOTvpx.a libvpx.a
mv libNOTvpx_g.a libvpx_g.a

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/vpx,%{_libdir}}

install -d outdir
%{__make} -C build install \
	DIST_DIR=$(pwd)/outdir

mv outdir/bin/{simple_decoder,vp8_simple_decoder}
mv outdir/bin/{twopass_encoder,vp8_twopass_encoder}
install -p outdir/bin/* $RPM_BUILD_ROOT%{_bindir}

ln -s libvpx.so.0.0.0 build/libvpx.so.0.0
ln -s libvpx.so.0.0.0 build/libvpx.so.0
install -p build/libvpx.so* $RPM_BUILD_ROOT%{_libdir}

cp -a outdir/include/*.h $RPM_BUILD_ROOT%{_includedir}/vpx
cp -a outdir/lib/*.a $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/libvpx.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libvpx.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvpx*.so
%{_includedir}/vpx

%files static
%defattr(644,root,root,755)
%{_libdir}/libvpx.a
