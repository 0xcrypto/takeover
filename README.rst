takeover.py
===========

This small script tries to detect subdomain takeovers from a list of
domains. Fingerprints are taken from
https://github.com/EdOverflow/can-i-take-over-xyz.

|Twitter|

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

    subfinder -d "example.com" -silent | takeover

Automation:

Creating a automated scan server:

.. code:: python

    import json, asyncio, pickle, os
    from pathlib import Path
    from takeover.takeover import takeover

    home = str(Path.home())

    # config is an dictionary. See ~/.config/takeover/config.json for structure
    config = json.load(open(home + "/.config/takeover/config.json"))

    # Do not forget to replace pointer to fingerprints with the valid data. See ~/.config/takeover/fingerprints.json for structure
    config['fingerprints'] = json.load(open(home + "/.config/takeover/fingerprints.json"))

    async def loop():
        print("Starting infinite loop:")
        while True:
                takeoverObject = takeover(config)
                try:
                    takeoverObject.found = pickle.load(open("found.pickle", 'rb'))
                except FileNotFoundError:
                    print("No old data found.", end="\r")
                
                try:
                    with open("subdomains.txt") as subdomainFile:
                        subdomains = enumerate(subdomainFile)
                        await takeoverObject.checkHosts(subdomains)
                except FileNotFoundError:
                    continue

                with open("found.pickle", 'wb') as foundFile:
                    pickle.dump(takeoverObject.found, foundFile)

                os.remove("subdomains.txt")
                print("Enumerated all targets in subdomains.txt for takeover")

    asyncio.run(loop())

The above automation script can be used along with any subdomain enumeration tool:

::

    subfinder -d example.com -o subdomains.txt

and the running infinite loop will automatically detect `subdomains.txt` file and start looking for takeovers. After completion, it also deletes the subdomains.txt so that you can add new targets. Obviously, you can tweak it however you want.

How it Works
------------

-  Matches CNAME against takeover-able services
-  If CNAME found, matches fingerprints in the body.

Note
----

-  The output is a lot verbose so it is recommended to use a discord
   webhook to get notified. I am planning to change it in a major
   update.
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

.. |Twitter| image:: https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2F0xcrypto%2Ftakeover
   :target: https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2F0xcrypto%2Ftakeover
