Summary:	Web browser
Name:		firefox
Version:	26.0
Release:	2
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		X11/Applications
Source0:	ftp://ftp.mozilla.org/pub/firefox/releases/%{version}/source/firefox-%{version}.source.tar.bz2
# Source0-md5:	91ce51cc6474f1269484e5327643a59c
Source1:	ftp://ftp.mozilla.org/pub/firefox/releases/26.0/linux-i686/xpi/de.xpi
# Source1-md5:	d659f1c611f5c94311f9f91e1767673f
Source2:	ftp://ftp.mozilla.org/pub/firefox/releases/26.0/linux-i686/xpi/pl.xpi
# Source2-md5:	07aa1d3b1e9a3959762ee326ac0c17bc
Source100:	vendor.js
Patch0:		%{name}-install-dir.patch
Patch1:		%{name}-virtualenv.patch
URL:		http://www.mozilla.org/projects/firefox/
BuildRequires:	OpenGL-devel
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	cairo-devel
BuildRequires:	gtk+-devel
BuildRequires:	hunspell-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libnotify-devel
BuildRequires:	libpng-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libvpx-devel
BuildRequires:	nspr-devel >= 1:4.10
BuildRequires:	nss-devel >= 1:3.15.1
BuildRequires:	pango-devel
BuildRequires:	perl-modules
BuildRequires:	pkg-config
BuildRequires:	sed
BuildRequires:	sqlite3-devel >= 3.7.15.2
BuildRequires:	startup-notification-devel
BuildRequires:	xorg-libXcursor-devel
BuildRequires:	xorg-libXft-devel
BuildRequires:	zip
BuildRequires:	zlib-devel
BuildRequires:  xulrunner-devel >= %{version}
Requires(post,postun):	/usr/bin/gtk-update-icon-cache
Requires(post,postun):	desktop-file-utils
Requires(post,postun):	hicolor-icon-theme
# for audio and video playback
Suggests:	gstreamer010-ffmpeg
Suggests:	gstreamer010-plugins-bad
Suggests:	gstreamer010-plugins-base
Suggests:	gstreamer010-plugins-good
Suggests:	gstreamer010-plugins-ugly
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Web browser.

%prep
%setup -qc

cd mozilla-release
%patch0 -p1
%patch1 -p1

%build
cd mozilla-release
cp -f %{_datadir}/automake/config.* build/autoconf

cat << 'EOF' > .mozconfig
. $topsrcdir/browser/config/mozconfig

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj-%{_target_cpu}
#
ac_add_options --host=%{_host}
ac_add_options --build=%{_host}
#
ac_add_options --libdir=%{_libdir}
ac_add_options --prefix=%{_prefix}
#
ac_add_options --disable-crashreporter
ac_add_options --disable-installer
ac_add_options --disable-javaxpcom
ac_add_options --disable-logging
ac_add_options --disable-mochitest
ac_add_options --disable-tests
ac_add_options --disable-updater
#
ac_add_options --enable-safe-browsing
#
ac_add_options --disable-debug
ac_add_options --disable-pedantic
ac_add_options --disable-strip
ac_add_options --disable-strip-install
#
ac_add_options --enable-optimize
#
ac_add_options --disable-gnomeui
ac_add_options --disable-gnomevfs
ac_add_options --enable-gio
ac_add_options --enable-gstreamer
ac_add_options --enable-startup-notification
#
ac_add_options --enable-system-cairo
ac_add_options --enable-system-hunspell
ac_add_options --enable-system-lcms
ac_add_options --enable-system-sqlite
ac_add_options --enable-system-ffi
ac_add_options --enable-system-pixman
ac_add_options --with-pthreads
ac_add_options --with-system-bz2
ac_add_options --with-system-jpeg
ac_add_options --with-system-libevent
ac_add_options --with-system-libvpx
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
ac_add_options --with-system-png
ac_add_options --with-system-zlib
ac_add_options --with-libxul-sdk=$(pkg-config --variable=sdkdir libxul)
#
ac_add_options --enable-official-branding
#
export BUILD_OFFICIAL=1
export MOZILLA_OFFICIAL=1
mk_add_options BUILD_OFFICIAL=1
mk_add_options MOZILLA_OFFICIAL=1

EOF

export CFLAGS="%{rpmcflags}"
export CXXFLAGS="%{rpmcflags}"
export LDFLAGS="%{rpmldflags}"

# i686 build broken:
#
# Traceback (most recent call last):
# File "./config.status", line 947, in <module>
# config_status(**args)
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/build/ConfigStatus.py", line 117, in config_status
# log_manager.add_terminal_logging(level=log_level)
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/python/mach/mach/logging.py", line 181, in add_terminal_logging
# if self.terminal:
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/python/mach/mach/logging.py", line 153, in terminal
# terminal = blessings.Terminal(stream=sys.stdout)
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/python/blessings/blessings/__init__.py", line 98, in __init__
# self._init_descriptor)
# _curses.error: setupterm: could not find terminal
#
# workaround:
export TERM=xterm

%{__make} -f client.mk configure
%{__make} -f client.mk build		\
	CC="%{__cc}"			\
	CXX="%{__cxx}"			\
	MOZ_MAKE_FLAGS=%{?_smp_mflags}	\
	STRIP="/bin/true"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_desktopdir}}	\
	$RPM_BUILD_ROOT%{_iconsdir}/hicolor/{16x16,22x22,24x24,32x32,48x48,256x256}/apps

cd mozilla-release

install -D %{SOURCE100} $RPM_BUILD_ROOT%{_libdir}/firefox/browser/defaults/preferences/vendor.js

%{__make} -j1 -f client.mk install	\
	DESTDIR=$RPM_BUILD_ROOT		\
	MOZ_PKG_FATAL_WARNINGS=0	\
	STRIP="/bin/true"

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_libdir}/%{name}/browser/extensions/langpack-de@firefox.mozilla.org.xpi
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_libdir}/%{name}/browser/extensions/langpack-pl@firefox.mozilla.org.xpi

ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries
ln -s %{_libdir}/browser-plugins $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins
ln -s ../xulrunner $RPM_BUILD_ROOT%{_libdir}/%{name}/xulrunner

for i in 16 22 24 32 48 256; do
    install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps
    cp browser/branding/official/default${i}.png \
    	$RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/firefox.png
done

cat > $RPM_BUILD_ROOT%{_desktopdir}/%{name}.desktop <<EOF
[Desktop Entry]
Name=Firefox
GenericName=Web Browser
Comment=Mozilla.org web browser
Exec=firefox %u
Icon=%{name}
StartupNotify=true
Terminal=false
Type=Application
Categories=GTK;Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
EOF

rm -rf $RPM_BUILD_ROOT%{_bindir}/firefox
cat > $RPM_BUILD_ROOT%{_bindir}/firefox <<EOF
#!/bin/sh
exec %{_libdir}/firefox/firefox "\$@"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_icon_cache hicolor
%update_desktop_database

%postun
%update_icon_cache hicolor
%update_desktop_database

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/firefox
%attr(755,root,root) %{_libdir}/firefox/firefox
%attr(755,root,root) %{_libdir}/firefox/run-mozilla.sh
%attr(755,root,root) %{_libdir}/firefox/webapprt-stub

%dir %{_libdir}/firefox
%dir %{_libdir}/firefox/browser

%dir %{_libdir}/firefox/browser/components
%attr(755,root,root) %{_libdir}/firefox/browser/components/libbrowsercomps.so
%{_libdir}/firefox/browser/components/components.manifest

%dir %{_libdir}/firefox/browser/extensions
%lang(de) %{_libdir}/firefox/browser/extensions/langpack-de@firefox.mozilla.org.xpi
%lang(pl) %{_libdir}/firefox/browser/extensions/langpack-pl@firefox.mozilla.org.xpi
%{_libdir}/firefox/browser/extensions/{972ce4c6-7e08-4474-a285-3208198ce6fd}

# dirs
%{_libdir}/firefox/browser/chrome
%{_libdir}/firefox/browser/icons
%{_libdir}/firefox/browser/searchplugins
%{_libdir}/firefox/browser/defaults
%{_libdir}/firefox/plugins
%{_libdir}/firefox/dictionaries
%{_libdir}/firefox/webapprt
%{_libdir}/firefox/xulrunner

# misc files
%{_libdir}/firefox/browser/blocklist.xml
%{_libdir}/firefox/browser/chrome.manifest
%{_libdir}/firefox/browser/omni.ja
%{_libdir}/firefox/application.ini
%{_libdir}/firefox/removed-files


%{_desktopdir}/firefox.desktop
%{_iconsdir}/hicolor/*/apps/*.png

