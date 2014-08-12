#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	ffi
Summary:	%{modname} - Foreign Function Interface
Name:		%{php_name}-pecl-%{modname}
Version:	0.4
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-0.3.tgz
# Source0-md5:	3ec0153672981bf7a8895758264bf3b4
Patch0:		branch.diff
URL:		http://pecl.php.net/package/ffi/
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(ffi) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
FFI is a multi-platform extension for PHP 5 that allows you to bind to
functions from arbitrary shared libraries and call them.

%prep
%setup -qc
mv %{modname}-*/* .
%patch0 -p0

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CREDITS EXPERIMENTAL
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%{_examplesdir}/%{name}-%{version}
