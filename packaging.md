Quick notes on packaging etc
============================

After adding files

  dpkg-source --commit
  
Build the package

  dpkg-buildpackage -us -uc
  
Install (test) the package

  sudo dpkg -i bitcoinwifi_0.1-1_all.deb
  
Remove the package files

  sudo dpkg -r bitcoinwifi
  
