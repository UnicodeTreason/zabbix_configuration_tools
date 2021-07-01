# zabbix_configuration_tools

## Usage

Point to a dir containing the desired state template files, most likely this is a cloned git repo.

```shell
./zabbix_configuration_tools/zct.py /mnt/c/data/git/zabbix_templates/
```

Or don't, and just cache your Zabbix templates to disk

```shell
./zabbix_configuration_tools/zct.py ""
```

This initial version just prints the Diff out

```shell
2021-07-01 19:09:07,685 INFO zct[3844]: Starting zct
2021-07-01 19:09:08,176 INFO zct[3844]: Connected to Zabbix API Version 5.2.6
2021-07-01 19:09:08,332 INFO zct[3844]: Caching current state for comparison
2021-07-01 19:09:10,543 INFO zct[3844]: Reading desired state for comparison
2021-07-01 19:09:10,556 INFO zct[3844]: Comparing states
Template: Linux CPU SNMP Dev1
{'values_changed': {"root['zabbix_export']['date']": {'new_value': '2021-07-01T09:57:25Z', 'old_value': '2021-07-01T11:09:11Z'}}}
Template: Connection - IETF ICMP Ping
{'values_changed': {"root['zabbix_export']['date']": {'new_value': '2021-05-31T10:15:40Z', 'old_value': '2021-07-01T11:09:12Z'}}}
Template: Linux CPU SNMP Dev2
{'values_changed': {"root['zabbix_export']['date']": {'new_value': '2021-07-01T09:57:27Z', 'old_value': '2021-07-01T11:09:13Z'}}}
Template: Linux CPU SNMP Dev3
{'values_changed': {"root['zabbix_export']['date']": {'new_value': '2021-07-01T09:57:27Z', 'old_value': '2021-07-01T11:09:13Z'}}}
```
