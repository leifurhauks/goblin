.. goblin documentation master file, created by
   sphinx-quickstart on Mon Mar 21 11:22:36 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================
:py:mod:`Goblin<goblin>`
========================

Goblin - Python Object Graph Mapper for the `TinkerPop3`_ `Gremlin Server`_

As Gremlin approached The TinkerPop, ``mogwai`` felt left behind and the closer
he got, the more his world dissolved. He realized that all that he realized was
just a realization and that all realized realizations are just as real as the
need to evolve into something else - ``goblin`` was born...

Releases
========
The latest release of :py:mod:`Goblin<goblin>` is **0.0.2** *(coming soon)*.

Requirements
============

:py:mod:`Goblin<goblin>` uses :py:mod:`gremlinclient` to communicate with the
`Gremlin Server`_, and can use  a variety of client/library combinations
that work with different versions of Python. See the :py:mod:`gremlinclient`
docs for more information.

`Tornado`_

- Python 2.7+

`aiohttp`_

- Python 3.4+

`Tornado`_ w/`Asyncio`_

- Python 3.3+

`Tornado`_ w/`Trollius`_

- Python 2.7

:py:mod:`Goblin<goblin>` aims to provide full support for all `TinkerPop3`_ enabled
graph databases; however, it is currently only tested against `Titan:db`_ 1.x.
This project is under active development, and early releases should be considered
alpha as the API is not yet entirely stable.

Installation
============
Install using pip::

    $ pip install goblin

.. _getting-started:

Getting Started
===============

A simple example using the default Tornado client with Python 2.7+::

    from tornado import gen
    from tornado.ioloop import IOLoop
    from goblin import properties
    from goblin import connection
    from goblin.models import Vertex, Edge, V


    class User(Vertex):
        name = properties.String()


    class Follows(Edge):
        pass


    @gen.coroutine
    def go():
        goblin = yield User.create(name="Goblin")
        gremlin = yield User.create(name="Gremlin")
        gob_follows_grem = yield Follows.create(goblin, gremlin)
        # Find Gremlin's followers
        stream = yield V(gremlin).in_step().get()  # `in` is a reserved word
        followers = yield stream.read()
        return followers


    connection.setup("ws://localhost:8182")
    loop = IOLoop.current()
    try:
      followers = loop.run_sync(go)
    finally:
      loop.close()
      connection.tear_down()


Contributing
------------
:py:mod:`Goblin<goblin>` is under active development on Github, and contributions are welcome.
More guidelines coming soon....


Contents:

.. toctree::
   :maxdepth: 2

   usage
   websocket_client
   schema_management
   integration
   modules

.. _`Titan:db`: http://s3.thinkaurelius.com/docs/titan/1.0.0/index.html
.. _Tinkerpop3: http://tinkerpop.incubator.apache.org/
.. _Gremlin Server: http://tinkerpop.apache.org/docs/3.1.1-incubating/reference/#gremlin-server
.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _aiohttp: http://aiohttp.readthedocs.org/en/stable/
.. _Tornado: http://www.tornadoweb.org/en/stable/
.. _Github: https://github.com/ZEROFAIL/goblin/issues
.. _Trollius: http://trollius.readthedocs.org/
.. _requests-futures: https://pypi.python.org/pypi/requests-futures
.. _Pulsar: https://pythonhosted.org/pulsar/
.. _`on Github`: https://github.com/ZEROFAIL/goblin

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
