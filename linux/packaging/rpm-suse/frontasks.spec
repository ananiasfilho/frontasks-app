%define _work /work

Name: frontasks
Version: 0.1.0
Release: 1
Summary: Painel de tarefas flutuante e sempre-no-topo
License: AGPL-3.0-or-later
URL: https://github.com/ananiasfilho/frontasks-app
BuildArch: noarch
# Nomes de pacote do openSUSE (diferem do Fedora): typelibs de
# introspection em vez dos metapacotes gtk3/keybinder3/xapps.
Requires: python3, python3-gobject, typelib-1_0-Gtk-3_0, typelib-1_0-Keybinder-3_0, typelib-1_0-XApp-1_0
%global debug_package %{nil}

%description
FronTasks e um painel de tarefas leve, sempre-no-topo, com bandeja e
atalho global, para Linux (GTK3). Porte do app macOS original.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{python3_sitelib}/frontasks
cp -r %{_work}/frontasks/* %{buildroot}%{python3_sitelib}/frontasks/
find %{buildroot}%{python3_sitelib}/frontasks -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
install -d %{buildroot}%{_datadir}/applications
install -m 644 %{_work}/data/frontasks.desktop %{buildroot}%{_datadir}/applications/
install -d %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
install -m 644 %{_work}/frontasks/data/icons/frontasks.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/
cat > %{buildroot}%{_bindir}/frontasks <<'PYEOF'
#!/usr/bin/env python3
import sys
from frontasks.__main__ import main
sys.exit(main())
PYEOF
chmod 755 %{buildroot}%{_bindir}/frontasks

%files
%{_bindir}/frontasks
%{python3_sitelib}/frontasks
%{_datadir}/applications/frontasks.desktop
%{_datadir}/icons/hicolor/256x256/apps/frontasks.png

%post
gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
update-desktop-database -q %{_datadir}/applications >/dev/null 2>&1 || :

%changelog
* Sat Jul 18 2026 Ananias Filho <kram3r@gmail.com> - 0.1.0-1
- Pacote inicial (openSUSE Leap)
