# hass-evnotify
Home Assistant component for EVNotify

## Install

 - Clone this repo into `config/custom_components/evnotify`
 - Get akey and password from evnotify
 - Add something like this to `configuration.yaml`
```
- platform: evnotify
  akey: 126gef
  password: !secret evnotify_pass
  scan_interval: 300
```
 - Restart HA