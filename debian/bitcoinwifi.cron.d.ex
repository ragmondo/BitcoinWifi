#
# Regular cron jobs for the bitcoinwifi package
#
0 4	* * *	root	[ -x /usr/bin/bitcoinwifi_maintenance ] && /usr/bin/bitcoinwifi_maintenance
