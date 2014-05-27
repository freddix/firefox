Summary:	Web browser
Name:		firefox
Version:	29.0.1
Release:	1
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		X11/Applications
Source0:	ftp://ftp.mozilla.org/pub/firefox/releases/%{version}/source/firefox-%{version}.source.tar.bz2
# Source0-md5:	ca37addc3a69ef30247e00375dd93cd0
Source1:	ftp://ftp.mozilla.org/pub/firefox/releases/%{version}/linux-i686/xpi/de.xpi
# Source1-md5:	acc96484100af138cf1b6a0b06b68ac0
Source2:	ftp://ftp.mozilla.org/pub/firefox/releases/%{version}/linux-i686/xpi/pl.xpi
# Source2-md5:	e91cd800528e3e9b9628c03affb646da
Source100:	vendor.js
Patch0:		%{name}-install-dir.patch
Patch1:		%{name}-hunspell.patch
Patch2:		%{name}-virtualenv.patch
URL:		http://www.mozilla.org/projects/firefox/
BuildRequires:	OpenGL-devel
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	cairo-devel >= 1.10.2-2
BuildRequires:	gstreamer010-plugins-base-devel
BuildRequires:	gtk+-devel
BuildRequires:	hunspell-devel
BuildRequires:	icu-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libnotify-devel
BuildRequires:	libpng-devel >= 2:1.6.8
BuildRequires:	libstdc++-devel
BuildRequires:	libvpx-devel
BuildRequires:	nspr-devel >= 1:4.10.4
BuildRequires:	nss-devel >= 1:3.16
BuildRequires:	pango-devel
BuildRequires:	perl-modules
BuildRequires:	pkg-config
BuildRequires:	python-devel-src
BuildRequires:	sed
BuildRequires:	sqlite3-devel >= 3.8.2
BuildRequires:	startup-notification-devel
BuildRequires:	xorg-libXcursor-devel
BuildRequires:	xorg-libXft-devel
BuildRequires:	xorg-xserver-Xvfb
BuildRequires:	zip
BuildRequires:	zlib-devel
Requires(post,postun):	/usr/bin/gtk-update-icon-cache
Requires(post,postun):	desktop-file-utils
Requires(post,postun):	hicolor-icon-theme
Requires:	nspr >= 1:4.10.4
Requires:	nss >= 1:3.16
# for audio and video playback
Suggests:	gstreamer010-ffmpeg
Suggests:	gstreamer010-plugins-bad
Suggests:	gstreamer010-plugins-base
Suggests:	gstreamer010-plugins-good
Suggests:	gstreamer010-plugins-ugly
Obsoletes:	xulrunner
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# bug680547
%define		specflags	-mno-avx

%description
Web browser.

%prep
%setup -qc

cd mozilla-release
%patch0 -p1
%patch1 -p1
%patch2 -p1

# use system headers
%{__rm} extensions/spellcheck/hunspell/src/*.hxx
echo 'LOCAL_INCLUDES += $(MOZ_HUNSPELL_CFLAGS)' >> extensions/spellcheck/src/Makefile.in

# find ../../dist/sdk -name "*.pyc" | xargs rm
# rm: missing operand
%{__sed} -i "s|xargs rm|xargs rm -f|g" toolkit/mozapps/installer/packager.mk

%build
cd mozilla-release
cp -f %{_datadir}/automake/config.* build/autoconf

cat << 'EOF' > .mozconfig
. $topsrcdir/browser/config/mozconfig

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj-%{_target_cpu}
mk_add_options PROFILE_GEN_SCRIPT='$(PYTHON) $(MOZ_OBJDIR)/_profile/pgo/profileserver.py 10'
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
ac_add_options --enable-url-classifier
#
ac_add_options --enable-optimize
#
ac_add_options --disable-gnomeui
ac_add_options --disable-gnomevfs
ac_add_options --enable-gio
ac_add_options --enable-gstreamer
ac_add_options --enable-startup-notification
#
#ac_add_options --enable-system-cairo
ac_add_options --enable-system-ffi
ac_add_options --enable-system-hunspell
ac_add_options --enable-system-lcms
ac_add_options --enable-system-pixman
ac_add_options --enable-system-sqlite
ac_add_options --with-pthreads
ac_add_options --with-system-bz2
ac_add_options --with-system-icu
ac_add_options --with-system-jpeg
ac_add_options --with-system-libevent
ac_add_options --with-system-libvpx
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
ac_add_options --with-system-png
ac_add_options --with-system-zlib
#
ac_add_options --enable-official-branding
#
export BUILD_OFFICIAL=1
export MOZILLA_OFFICIAL=1
export MOZ_UA_BUILDID=20100101
mk_add_options BUILD_OFFICIAL=1
mk_add_options MOZILLA_OFFICIAL=1

EOF

# generate smaller debug files
export CFLAGS="%(echo %{rpmcflags} | sed 's/ -g2/ -g1/g')"
export CXXFLAGS="%(echo %{rpmcxxflags} | sed 's/ -g2/ -g1/g')"
export LDFLAGS="%{rpmldflags} -Wl,-rpath,%{_libdir}/firefox"

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

# Traceback (most recent call last):
#  File "/usr/lib/python2.7/runpy.py", line 162, in _run_module_as_main
#    "__main__", fname, loader, pkg_name)
#  File "/usr/lib/python2.7/runpy.py", line 72, in _run_code
#    exec code in run_globals
#  File "/home/users/builder/rpm/BUILD/xulrunner-29.0/mozilla-release/python/mozbuild/mozbuild/action/webidl.py", line 7, in <module>
#    from mozwebidlcodegen import BuildSystemWebIDL
#  File "/home/users/builder/rpm/BUILD/xulrunner-29.0/mozilla-release/dom/bindings/mozwebidlcodegen/__init__.py", line 20, in <module>
#    from mozbuild.base import MozbuildObject
#  File "/home/users/builder/rpm/BUILD/xulrunner-29.0/mozilla-release/python/mozbuild/mozbuild/base.py", line 17, in <module>
#    from mach.mixin.process import ProcessExecutionMixin
#  File "/home/users/builder/rpm/BUILD/xulrunner-29.0/mozilla-release/python/mach/mach/mixin/process.py", line 29, in <module>
#    raise Exception('Could not detect environment shell!')
# Exception: Could not detect environment shell!
# Makefile:72: recipe for target 'codegen.pp' failed
# make[5]: *** [codegen.pp] Error 1
export SHELL=/usr/bin/sh

export MOZ_PGO=1
%{__make} -f client.mk configure

export DISPLAY=:99
Xvfb -nolisten tcp -extension GLX -screen 0 1280x1024x24 $DISPLAY &

%{__make} -f client.mk \
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
	INSTALL_SDK=			\
	MOZ_PKG_FATAL_WARNINGS=0	\
	STRIP="/bin/true"

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_libdir}/%{name}/browser/extensions/langpack-de@firefox.mozilla.org.xpi
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_libdir}/%{name}/browser/extensions/langpack-pl@firefox.mozilla.org.xpi

ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries
ln -s %{_libdir}/browser-plugins $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins

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

rm -rf $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries
ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries

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
%attr(755,root,root) %{_libdir}/firefox/libmozalloc.so
%attr(755,root,root) %{_libdir}/firefox/libxul.so
%attr(755,root,root) %{_libdir}/firefox/mozilla-xremote-client
%attr(755,root,root) %{_libdir}/firefox/plugin-container

%dir %{_libdir}/firefox/browser
%dir %{_libdir}/firefox/browser/components
%attr(755,root,root) %{_libdir}/firefox/browser/components/libbrowsercomps.so
%{_libdir}/firefox/browser/components/components.manifest

%dir %{_libdir}/firefox/components
%attr(755,root,root) %{_libdir}/firefox/components/libdbusservice.so
%attr(755,root,root) %{_libdir}/firefox/components/libmozgnome.so
%{_libdir}/firefox/components/components.manifest

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

# misc files
%dir %{_libdir}/firefox/defaults/pref
%{_libdir}/firefox/defaults/pref/channel-prefs.js
%{_libdir}/firefox/application.ini
%{_libdir}/firefox/browser/blocklist.xml
%{_libdir}/firefox/browser/chrome.manifest
%{_libdir}/firefox/browser/omni.ja
%{_libdir}/firefox/chrome.manifest
%{_libdir}/firefox/dependentlibs.list
%{_libdir}/firefox/omni.ja
%{_libdir}/firefox/platform.ini
%{_libdir}/firefox/removed-files

%{_desktopdir}/firefox.desktop
%{_iconsdir}/hicolor/*/apps/*.png

