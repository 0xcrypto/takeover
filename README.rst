takeover.py
===========

This small script tries to detect subdomain takeovers from a list of
domains. Fingerprints are taken from
https://github.com/EdOverflow/can-i-take-over-xyz.

Installation
------------

::

    pip install takeover.py

Usage
-----

::

    takeover blog.example.com

Using with other tools:

::

    subfinder -d "example.com" | takeover

Using in python:

.. code:: python

    import json, asyncio
    from pathlib import Path
    from takeover import takeover

    home = str(Path.home())

    # config is an dictionary. See ~/.config/takeover/config.json for structure
    config = json.load(open(home + "/.config/takeover/config.json"))

    # Do not forget to replace pointer to fingerprints with the valid data. See ~/.config/takeover/fingerprints.json for structure
    config['fingerprints'] = json.load(open(home + "/.config/takeover/fingerprints.json"))

    subdomains = ["blog.example.com", "services.example.com"]

    asyncio.run(takeover(config).checkHost(subdomains))

How it Works
------------

-  Matches CNAME against takeover-able services
-  If CNAME found, matches fingerprints in the body.

Note
----

-  As I use discord a lot, this script is programmed to notify using
   discord webhooks. So you will need to have a discord server and
   create a webhook to use in it.
-  If you need some extra features, feel free to submit a new issue on
   GitHub.

License
-------

`LICENSE.md <LICENSE.md>`__

Disclaimer
----------

I make guns, I sell guns, I give away guns but I take no responsibility
of who dies with the guns.

*Legally speaking, What you do with this has nothing to do with me. I am
not responsible for your actions.*
