.. _takeoverpy:

takeover.py
===========

A script to test for subdomain takeovers from a list of domains.
Fingerprints are taken from
https://github.com/EdOverflow/can-i-take-over-xyz.

|Twitter|

Installation
------------

::

   pip install takeover.py

After installation, make sure to configure the config.json file. You can
also copy it from the github repository and use with ``--config`` flag.

Usage
-----

A single target

::

   echo blog.example.com | takeover -

Multiple Targets:

.. code:: bash

   subfinder -d "example.com" -silent | takeover -

   # or
   subfinder -d "example.com" -silent | takeover /dev/stdin

Notifications:

.. code:: bash

   subfinder -d "example.com" -silent | takeover - --notify Discord

Note
----

-  The output is a lot verbose so it is recommended to use a third party
   webhook service like discord, slack to get notified.
-  Some fingerprints are not well formatted to be matched. For example,
   in WordPress, the fingerprint is
   ``Do you want to register *.wordpress.com?``, however this is not an
   exact match and correct fingerprint should be
   ``Do you want to register <em>example.wordpress.com</em>?``. To fix
   this, you can give your own file for fingerprints with either in
   ``config.json`` or with ``--services`` flag.

Contribute
----------

-  Feel free to submit a PR or new issues on GitHub.

License
-------

`LICENSE.md <LICENSE.md>`__

Disclaimer
----------

An excerpt from the License: "IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."

.. |Twitter| image:: https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2F0xcrypto%2Ftakeover
   :target: https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2F0xcrypto%2Ftakeover
