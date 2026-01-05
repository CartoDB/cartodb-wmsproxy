# ⚠️ ARCHIVED - This repository is no longer maintained

**This repository has been archived and is no longer actively maintained.**

This project was last updated on 2022-04-26 and is preserved for historical reference only.

- 🔒 **Read-only**: No new issues, pull requests, or changes will be accepted
- 📦 **No support**: This code is provided as-is with no support or updates
- 🔍 **For reference only**: You may fork this repository if you wish to continue development

For current CARTO projects and actively maintained repositories, please visit: https://github.com/CartoDB

---

WMSProxy
========

WMSProxy is a proxy that makes CartoDB user layers available as WMS and WMTS.
WMTProxy does this by creating MapProxy configurations based on the viz.json for a user. Configurations are created dynamically and are cached for a few minutes.

See example_config.py for an example WSGI configuration.

The WMS is available at: http://localhost/<username>/service?

The WMTS is available at: http://localhost/<username>/wmts/1.0.0/WMTSCapabilities.xml