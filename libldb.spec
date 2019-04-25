# Single python3 version in Fedora, python3_pkgversion macro not available
%{!?python3_pkgversion:%global python3_pkgversion 3}

%global with_python3 1

%global with_python2 1
%if 0%{?fedora} > 30
%global with_python2 0
%endif

%global talloc_version 2.1.11
%global tdb_version 1.3.14
%global tevent_version 0.9.36

Name: libldb
Version: 1.4.6
Release: 0.1%{?dist}
Summary: A schema-less, ldap like, API and database
Requires: libtalloc%{?_isa} >= %{talloc_version}
Requires: libtdb%{?_isa} >= %{tdb_version}
Requires: libtevent%{?_isa} >= %{tevent_version}
License: LGPLv3+
URL: https://ldb.samba.org/
Source: https://www.samba.org/ftp/ldb/ldb-%{version}.tar.gz

BuildRequires: gcc
BuildRequires: libtalloc-devel >= %{talloc_version}
BuildRequires: libtdb-devel >= %{tdb_version}
BuildRequires: libtevent-devel >= %{tevent_version}
BuildRequires: lmdb-devel >= 0.9.16
BuildRequires: popt-devel
BuildRequires: libxslt
BuildRequires: docbook-style-xsl
BuildRequires: python2-devel
BuildRequires: python2-tdb
BuildRequires: python2-talloc-devel
BuildRequires: python2-tevent
BuildRequires: doxygen
BuildRequires: openldap-devel
BuildRequires: libcmocka-devel >= 1.1.1

Provides: bundled(libreplace)

%if %{with_python3}
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-tdb
BuildRequires: python%{python3_pkgversion}-talloc-devel
BuildRequires: python%{python3_pkgversion}-tevent
%endif

# Patches
Patch0001: 0002-ldb-Run-at-least-some-tests-on-32-bit-machines.patch

%description
An extensible library that implements an LDAP like API to access remote LDAP
servers, or use local tdb databases.

%package -n ldb-tools
Summary: Tools to manage LDB files
Requires: libldb%{?_isa} = %{version}-%{release}

%description -n ldb-tools
Tools to manage LDB files

%package devel
Summary: Developer tools for the LDB library
Requires: libldb%{?_isa} = %{version}-%{release}
Requires: libtdb-devel%{?_isa} >= %{tdb_version}
Requires: libtalloc-devel%{?_isa} >= %{talloc_version}
Requires: libtevent-devel%{?_isa} >= %{tevent_version}
Requires: pkgconfig

%description devel
Header files needed to develop programs that link against the LDB library.

%package -n python2-ldb
Summary: Python bindings for the LDB library
Requires: libldb%{?_isa} = %{version}-%{release}
Requires: python2-tdb%{?_isa} >= %{tdb_version}

Provides: pyldb = %{version}-%{release}
Provides: pyldb%{?_isa} = %{version}-%{release}
Obsoletes: pyldb < 1.1.26-2
%{?python_provide:%python_provide python2-ldb}

%description -n python2-ldb
Python bindings for the LDB library

%package -n python2-ldb-devel
Summary: Development files for the Python bindings for the LDB library
Requires: python2-ldb%{?_isa} = %{version}-%{release}
Requires: python-ldb-devel-common%{?_isa} = %{version}-%{release}

Provides: pyldb-devel = %{version}-%{release}
Provides: pyldb-devel%{?_isa} = %{version}-%{release}
Obsoletes: pyldb-devel < 1.1.26-2
%{?python_provide:%python_provide python2-ldb-devel}

%description -n python2-ldb-devel
Development files for the Python bindings for the LDB library

%package -n python-ldb-devel-common
Summary: Common development files for the Python bindings for the LDB library

Provides: pyldb-devel%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python2-ldb-devel}

%description -n python-ldb-devel-common
Development files for the Python bindings for the LDB library.
This package includes files that are not specific to a Python version.

%if %{with_python3}

%package -n python%{python3_pkgversion}-ldb
Summary: Python bindings for the LDB library
Requires: libldb%{?_isa} = %{version}-%{release}
Requires: python%{python3_pkgversion}-tdb%{?_isa} >= %{tdb_version}

%{?python_provide:%python_provide python%{python3_pkgversion}-ldb}

%description -n python%{python3_pkgversion}-ldb
Python bindings for the LDB library

%package -n python%{python3_pkgversion}-ldb-devel
Summary: Development files for the Python bindings for the LDB library
Requires: python%{python3_pkgversion}-ldb%{?_isa} = %{version}-%{release}
Requires: python-ldb-devel-common%{?_isa} = %{version}-%{release}

%{?python_provide:%python_provide python%{python3_pkgversion}-ldb-devel}

%description -n python%{python3_pkgversion}-ldb-devel
Development files for the Python bindings for the LDB library

%endif

%prep
%setup -q -n ldb-%{version}
%patch0001 -p3

%build

%if %{with_python3}
PY3_CONFIG_FLAGS=--extra-python=%{__python3}
%else
PY3_CONFIG_FLAGS=""
%endif

# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1217376
export python_LDFLAGS=""

pathfix.py -n -p -i %{__python2} buildtools/bin/waf

%configure --disable-rpath \
           --disable-rpath-install \
           --bundled-libraries=NONE \
           --builtin-libraries=replace \
           --with-modulesdir=%{_libdir}/ldb/modules \
           $PY3_CONFIG_FLAGS \
           --with-privatelibdir=%{_libdir}/ldb

make %{?_smp_mflags} V=1
doxygen Doxyfile

%check
make %{?_smp_mflags} check

%install
make install DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/libldb.a

# Shared libraries need to be marked executable for
# rpmbuild to strip them and include them in debuginfo
find $RPM_BUILD_ROOT -name "*.so*" -exec chmod -c +x {} \;

# Install API docs
cp -a apidocs/man/* $RPM_BUILD_ROOT/%{_mandir}

# LDB 1.1.8+ bug: remove manpage named after full
# file path
rm -f $RPM_BUILD_ROOT/%{_mandir}/man3/_*

#%%ldconfig_scriptlets
%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%dir %{_libdir}/ldb
%{_libdir}/libldb.so.*
%{_libdir}/ldb/libldb-key-value.so
# lmdb is not supported on 32 bit architectures
%if 0%{?__isa_bits} == 64
%{_libdir}/ldb/libldb-mdb-int.so
%endif
%dir %{_libdir}/ldb/modules
%dir %{_libdir}/ldb/modules/ldb
%{_libdir}/ldb/modules/ldb/*.so

%files -n ldb-tools
%{_bindir}/ldbadd
%{_bindir}/ldbdel
%{_bindir}/ldbedit
%{_bindir}/ldbmodify
%{_bindir}/ldbrename
%{_bindir}/ldbsearch
%{_libdir}/ldb/libldb-cmdline.so
%{_mandir}/man1/ldbadd.1.*
%{_mandir}/man1/ldbdel.1.*
%{_mandir}/man1/ldbedit.1.*
%{_mandir}/man1/ldbmodify.1.*
%{_mandir}/man1/ldbrename.1.*
%{_mandir}/man1/ldbsearch.1.*

%files devel
%{_includedir}/ldb_module.h
%{_includedir}/ldb_handlers.h
%{_includedir}/ldb_errors.h
%{_includedir}/ldb_version.h
%{_includedir}/ldb.h
%{_libdir}/libldb.so

%{_libdir}/pkgconfig/ldb.pc
%{_mandir}/man3/ldb*.gz
%{_mandir}/man3/ldif*.gz

%files -n python2-ldb
%{python2_sitearch}/ldb.so
%{_libdir}/libpyldb-util.so.1*
%{python2_sitearch}/_ldb_text.py*

%files -n python2-ldb-devel
%{_libdir}/libpyldb-util.so
%{_libdir}/pkgconfig/pyldb-util.pc

%files -n python-ldb-devel-common
%{_includedir}/pyldb.h
%{_mandir}/man*/Py*.gz

#%%ldconfig_scriptlets -n python2-ldb
%post -n python2-ldb -p /sbin/ldconfig
%postun -n python2-ldb -p /sbin/ldconfig

%if %{with_python3}
%files -n python%{python3_pkgversion}-ldb
%{python3_sitearch}/ldb.cpython-*.so
%{_libdir}/libpyldb-util.cpython-*.so.1*
%{python3_sitearch}/_ldb_text.py
%{python3_sitearch}/__pycache__/_ldb_text.cpython-*.py*

%files -n python%{python3_pkgversion}-ldb-devel
%{_libdir}/libpyldb-util.cpython-*.so
%{_libdir}/pkgconfig/pyldb-util.cpython-*.pc

#%%ldconfig_scriptlets -n python%{python3_pkgversion}-ldb
%post -n python%{python3_pkgversion}-ldb -p /sbin/ldconfig
%postun -n python%{python3_pkgversion}-ldb -p /sbin/ldconfig
%endif

%changelog
* Thu Apr 25 2019 Nico Kadel-Garcia <nkadel@gmail.com> - 1.4.6-0.1
- Update python2/python3 logic to discard python2 for Fedora > 30

* Wed Apr 24 2019 Nico Kadel-Garcia <nkadel@gmail.com> - 1.4.6-0
- Update to 1.4.6
- Use pathfix.py and python3_pkgversion consistently for RHEL

* Thu Aug 16 2018 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.4.2-1
- New upstream release 1.4.2

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jul 12 2018 Jakub Hrozek <jhrozek@redhat.com> - 1.4.1-1
- New upstream release 1.4.1
- Apply a patch to hide local ABI symbols to avoid issues with new binutils
- Patch the waf script to explicitly call python2 as "env python" does not
  yield py2 anymore

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 1.4.0-2
- Rebuilt for Python 3.7

* Wed May 30 2018 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.4.0-1
- New upstream release 1.4.0
- Resolves: rhbz#1584450 - libldb-1.4.0 is available

* Thu May  3 2018 Jakub Hrozek <jhrozek@redhat.com> - 1.3.2-1
- New upstream release 1.3.3
- Resolves: rhbz#1574267 - libldb-1.3.3 is available
- Backport a patch from samba upstream to not require rpc.h

* Thu Mar 01 2018 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.3.2-2
- Disable link time optimisation for python3 related modules/libs
- Workaround for rhbz#1548822

* Thu Mar 01 2018 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.3.2-1
- New upstream release 1.3.2
- Resolves: rhbz#1550051 - libldb-1.3.2 is available

* Mon Feb 26 2018 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.3.1-6
- Use ldconfig scriptlets
- Add gcc to BuildRequires

* Sat Feb 24 2018 Florian Weimer <fweimer@redhat.com> - 1.3.1-5
- Another rebuild with new build flags

* Sat Feb 24 2018 Florian Weimer <fweimer@redhat.com> - 1.3.1-4
- Rebuild to pick up new Python build flags

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 1.3.1-2
- Rebuilt for switch to libxcrypt

* Sat Jan 13 2018 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.3.1
- New upstream release 1.3.1
- Resolves: rhbz#1534128 - libldb-1.3.1 is available

* Tue Jan 09 2018 Iryna Shcherbina <ishcherb@redhat.com> - 1.3.0-4
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Nov 30 2017 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.3.0-3
- Update spec file conditionals

* Sat Oct 21 2017 Lukas Slebodnik <lslebodn@fedoraproject.org> - 1.3.0-2
- Fix memory leak introduced in 1.3.0

* Fri Oct 20 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.3.0
- New upstream release 1.3.0
- Resolves: rhbz#1504361 - libldb-1.3.0 is available

* Mon Sep 11 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.2.2
- New upstream release 1.2.2
- Resolves: rhbz#1489418  - libldb-1.2.2 is available

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.2.1
- New upstream release 1.2.1
- Resolves: rhbz#1473988 - libldb-1.2.1 is available

* Thu Jul 06 2017 Andreas Schneider <asn@redhat.com> - 1.2.0-2
- Fix pyhton3 support

* Tue Jul  4 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.2.0
- New upstream release 1.2.0
- Resolves: rhbz#1467118 - libldb-1.2.0 is available

* Fri Jun 16 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.1.31-1
- New upstream release 1.1.31
- Resolves: rhbz#1462041 - libldb-1.1.31 is available

* Fri Jun  2 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.1.30-1
- New upstream release 1.1.30
- Resolves: rhbz#1458264 - libldb-1.1.30 is available

* Sat Apr 01 2017 Lukas Slebodnik <lslebodn@redhat.com> - 1.1.29-5
- rhbz#1401172 - Missing symbol versioning provided by libldb.so with strict CFLAGS
- Fix configure time detection with -Werror=implicit-function-declaration
  -Werror=implicit-int

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.29-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 1.1.29-3
- Rebuild for Python 3.6

* Tue Dec 06 2016 Adam Williamson <awilliam@redhat.com> - 1.1.29-2
- rebuild with reverted redhat-rpm-config to fix missing symbols

* Fri Dec  2 2016 Jakub Hrozek <jhrozek@redhat.com> - 1.1.29-1
- New upstream release 1.1.29
- Resolves: rhbz#1400738 - libldb-1.1.29 is available

* Fri Nov 25 2016 Jakub Hrozek <jhrozek@redhat.com> - 1.1.28-1
- New upstream release 1.1.28
- Resolves: rhbz#1398307 - libldb-1.1.28 is available

* Thu Jul 28 2016 Jakub Hrozek <jhrozek@redhat.com> - 1.1.27-1
- New upstream release 1.1.27
- Resolves: rhbz#1361163 - libldb-1.1.27 is available

* Thu Jul 21 2016 Lukas Slebodnik <lslebodn@redhat.com> - 1.1.26-4
- rhbz#1358281 - cannot install pyldb

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.26-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Jul 05 2016 Petr Viktorin <pviktori@redhat.com> - 1.1.26-2
- Package the Python3 bindings

* Mon Feb 22 2016 Jakub Hrozek <jhrozek@redhat.com> - 1.1.26-1
- New upstream release 1.1.26

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.25-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan  4 2016 Jakub Hrozek <jhrozek@redhat.com> - 1.1.25-1
- New upstream release 1.1.25

* Wed Dec 16 2015 Jakub Hrozek <jhrozek@redhat.com> - 1.1.24-1
- New upstream release 1.1.24
- Resolves: rhbz#1292070 - CVE-2015-5330 libldb: samba: Remote memory read
                           in Samba LDAP server [fedora-all]

* Wed Dec 16 2015 Jakub Hrozek <jhrozek@redhat.com> - 1.1.23-2
- Fix CVE-2015-5330

* Thu Nov 12 2015 Jakub Hrozek <jhrozek@redhat.com> - 1.1.23-1
- New upstream release 1.1.23

* Tue Aug 25 2015 Andreas Schneider <asn@redhat.com> - 1.1.21-1
- New upstream release 1.1.21

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jan 28 2015 Jakub Hrozek <jhrozek@redhat.com> - 1.1.20-1
- New upstream release 1.1.20

* Mon Jan  5 2015 Jakub Hrozek <jhrozek@redhat.com> - 1.1.19-1
- New upstream release 1.1.19

* Fri Dec  5 2014 Jakub Hrozek <jhrozek@redhat.com> - 1.1.18-1
- New upstream release 1.1.18

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.17-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 06 2014 Jakub Hrozek <jhrozek@redhat.com> - 1.1.17-2
- Fix the previous changelog entry

* Tue May 06 2014 Jakub Hrozek <jhrozek@redhat.com> - 1.1.17-1
- New upstream release 1.1.17

* Thu Jan 02 2014 Stephen Gallagher <sgallagh@redhat.com> - 1.1.16-4
- Enable building libldb LDAP interface module

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.16-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 08 2013 Jakub Hrozek <jhrozek@redhat.com> - 1.1.16-2
- Make the Requires arch-specific

* Tue Jul 02 2013 - Andreas Schneider <asn@redhat.com> - 1.1.16-1
- New upstream release 1.1.16

* Wed Jun 05 2013 Jakub Hrozek <jhrozek@redhat.com> - 1.1.15-3
- Relax pytdb requirement

* Thu Feb 07 2013 Jakub Hrozek <jhrozek@redhat.com> - 1.1.15-2
- The 1.1.15 rebase obsoletes the patch from 1.1.14-2

* Thu Feb 07 2013 Jakub Hrozek <jhrozek@redhat.com> - 1.1.15-1
- New upstream release 1.1.15

* Wed Jan 30 2013 Jakub Hrozek <jhrozek@redhat.com> - 1.1.14-2
- Add patch by Stephen Gallagher to include manual pages for
  ldb_connect() and several other functions.

* Sat Dec 01 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.1.14-1
- New upstream release 1.1.14

* Wed Oct 03 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.1.13-1
- New upstream release 1.1.13

* Mon Sep 03 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.1.12-1
- New upstream release 1.1.12

* Tue Aug 28 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.1.11-1
- New upstream release 1.1.11

* Fri Aug 10 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.1.10-1
- New upstream release 1.1.10

* Thu Aug 02 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.1.9-1
- New upstream release 1.1.9
- Required for Samba 4 Beta 5
- Ensure rename target does not exist before deleting old record
- Add parameter to avoid NULL format string flagged by -Werror=format

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 10 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.1.8-1
- New upstream release 1.1.8
- Required for latest Samba 4 beta
- Fixes for pyldb
- Revert to using tdb1 by default
- Drop support for tdb_compat
- CCAN is no longer built as a static library

* Tue May 22 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.1.6-1
- New upstream release 1.1.6
- Drop upstream patches
- Required for upcoming Samba 4 beta
- Explicitly build with tdb1 support

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Dec 09 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.1.4-1.1
- Do not build with multiple CPUs

* Tue Dec 06 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.1.4-1
- New upstream release
- Add ldb_module_error() routine
- Fedora: work around unreliable configure check for pytevent
- Drop patch to ignore --disable-silent-rules (included in tarball)

* Thu Dec 01 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.1.3-4
- Add patch to ignore --disable-silent-rules

* Wed Nov 23 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.1.3-3
- Add explicit mention of the bundled libreplace
- https://fedorahosted.org/fpc/ticket/120
- Add explicit mention of bundled libtdb_compat and libccan
- https://fedorahosted.org/fpc/ticket/119

* Mon Nov 21 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.1.3-2
- Build and install API documentation
- Build tdb_compat and ccan statically. They have no upstream releases to
  link against yet and their API is in flux. It is unsafe to make them
  public and shared at this time.

* Wed Nov 09 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.1.3-1
- New upstream release
- Required for building newer samba4 packages

* Tue Aug  2 2011 Simo Sorce <ssorce@redhat.com> - 1.1.0-1
- Update to 1.1.0
  (dependency for samba4 alpha16 snapshot)

* Tue Feb 22 2011 Simo Sorce <ssorce@redhat.com> - 1.0.2-1
- Update to 1.0.2
  (dependency for samba4 alpha15 snapshot)

* Fri Feb 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.0.0-2
- Disable rpath

* Fri Feb 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.0.0-1
- New upstream release 1.0.0
- SOname bump to account for module loading changes
- Rename libldb-tools to ldb-tools to make upgrades easier

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.22-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb 04 2011 Stephen Gallagher <sgallagh@redhat.com> - 0.9.22-8
- Fixes from package review
- Change Requires: on tools subpackage to be the exact version/release
- Remove unnecessary BuildRoot directive

* Mon Jan 17 2011 Stephen Gallagher <sgallagh@redhat.com> - 0.9.22-7
- Update to 0.9.22 (first independent release of libldb upstream)

