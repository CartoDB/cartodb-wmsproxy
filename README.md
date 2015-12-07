WMSProxy
========

WMSProxy is a proxy that makes CartoDB user layers available as WMS and WMTS.
WMTProxy does this by creating MapProxy configurations based on the viz.json for a user. Configurations are created dynamically and are cached for a few minutes.

See example_config.py for an example WSGI configuration.


Development
===========

Add an entry to your `/etc/hosts` file containing the line (replace
`<cartodb_account>` with an actual cartodb account name):

    127.0.0.1	<cartodb_account>.localhost


Then run `python ./dev_config.py` to start a dev server. While running:

- You can browse services at: `http://<username>.localhost/demo`
- WMS is available at: `http://<username>.localhost/service?`
- WMTS is available at: `http://<username>.localhost/wmts/1.0.0/WMTSCapabilities.xml`
