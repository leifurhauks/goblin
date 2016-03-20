from __future__ import unicode_literals
import logging
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from goblin.constants import (TORNADO_CLIENT_MODULE, AIOHTTP_CLIENT_MODULE,
                              SECURE_SCHEMES, INSECURE_SCHEMES)
from goblin.exceptions import GoblinConnectionError


logger = logging.getLogger(__name__)


# Global vars
Future = None
_connection_pool = None
_graph_name = None
_traversal_source = None
_loaded_models = []
_scheme = None
_netloc = None
_client_module = None


def execute_query(query, bindings=None, pool=None, graph_name=None,
                  traversal_source=None, username="", password="",
                  handler=None, *args, **kwargs):
    """
    Execute a raw Gremlin query with the given parameters passed in.

    :param str query: The Gremlin query to be executed
    :param dict bindings: Bindings for the Gremlin query
    :param `gremlinclient.pool.Pool` pool: Pool that provides connection used
        in query
    :param str graph_name: graph name as defined in server configuration.
        Defaults to "graph"
    :param str traversal_source: traversal source name as defined in the
        server configuration. Defaults to "g"
    :param str username: username as defined in the Tinkerpop credentials
        graph.
    :param str password: password for username as definined in the Tinkerpop
        credentials graph
    :param func handler: Handles preprocessing of query results

    :returns: Future
    """
    if Future is None:
        raise GoblinConnectionError(
            'Must call goblin.connection.setup before querying.')

    if pool is None:
        pool = _connection_pool

    if graph_name is None:
        graph_name = _graph_name

    if traversal_source is None:
        traversal_source = _traversal_source

    aliases = {"graph": graph_name, "g": traversal_source}

    future = Future()
    future_conn = pool.acquire()

    def on_connect(f):
        try:
            conn = f.result()
        except Exception as e:
            future.set_exception(e)
        else:
            stream = conn.send(
                query, bindings=bindings, aliases=aliases, handler=handler)
            future.set_result(stream)

    future_conn.add_done_callback(on_connect)

    return future


def tear_down():
    """Close the global connection pool."""
    if _connection_pool:
        return _connection_pool.close()


def setup(url, pool_class=None, graph_name='graph', traversal_source='g',
          username='', password='', pool_size=256, future_class=None,
          ssl_context=None, connector=None, loop=None):
    """
    This function is responsible for instantiating the global variables that
    provide :py:mod:`goblin` connection configuration params.

    :param str url: url for the Gremlin Server. Expected format:
        (ws|wss)://username:password@hostname:port/
    :param gremlinclient.pool.Pool pool_class: Pool class used to create
        global pool. If ``None`` trys to import
        :py:class:`tornado_client.Pool<gremlinclient.tornado_client.client.Pool>`,
        if this import fails, trys to import
        :py:class:`aiohttp_client.Pool<gremlinclient.aiohttp_client.client.Pool>`
    :param str graph_name: graph name as defined in server configuration.
        Defaults to "graph"
    :param str traversal_source: traversal source name as defined in the
        server configuration. Defaults to "g"
    :param str username: username as defined in the Tinkerpop credentials
        graph.
    :param str password: password for username as definined in the Tinkerpop
        credentials graph
    :param int pool_size: maximum number of connections allowed by global
        connection pool_size
    :param class future: type of Future. typically -
        :py:class:`asyncio.Future`, :py:class:`trollius.Future`, or
        :py:class:`tornado.concurrent.Future`
    :param ssl.SSLContext ssl_context: :py:class:`ssl.SSLContext` for secure
        protocol
    :param connector: connector used to establish :py:mod:`gremlinclient`
        connection. Overides ssl_context param.
    :param loop: io loop.
    """
    global Future
    global _connection_pool
    global _graph_name
    global _traversal_source
    global _scheme
    global _netloc
    global _client_module

    _graph_name = graph_name
    _traversal_source = traversal_source

    parsed_url = urlparse(url)
    _scheme = parsed_url.scheme
    _netloc = parsed_url.netloc

    pool_class = _get_pool_class(pool_class)

    try:
        _client_module = pool_class.__module__.split('.')[1]
    except IndexError:
        raise ValueError("Unknown client module.")

    if connector is None:
        connector = _get_connector(ssl_context)

    _connection_pool = pool_class(url,
                                  maxsize=pool_size,
                                  username=username,
                                  password=password,
                                  force_release=True,
                                  future_class=future_class,
                                  connector=connector)

    if future_class is None:
        future_class = _connection_pool.graph.future_class
    Future = future_class

    # Model/schema sync will run here as well as indexing


def _get_pool_class(pool_class):
    if pool_class is None:
        try:
            from gremlinclient.tornado_client import Pool
        except ImportError:
            try:
                from gremlinclient.aiohttp_client import Pool
            except ImportError:
                raise ImportError(
                    "Install appropriate client or pass pool explicitly")
        pool_class = Pool
    return pool_class


def _get_connector(ssl_context):
    if _scheme in SECURE_SCHEMES:
        if ssl_context is None:
            raise ValueError("Please pass ssl_context for secure protocol")

        if _client_module == AIOHTTP_CLIENT_MODULE:
            import aiohttp
            connector = aiohttp.TCPConnector(ssl_context=ssl_context,
                                             loop=loop)
        elif _client_module == TORNADO_CLIENT_MODULE:

            from tornado import httpclient
            from functools import partial
            connector = partial(
                httpclient.HTTPRequest, ssl_options=sslcontext)
        else:
            raise ValueError("Unknown client module")
    elif _scheme in INSECURE_SCHEMES:
        connector = None
    else:
        raise RuntimeError("Unknown protocol")
    return connector


def _add_model_to_space(model):
    global _loaded_models
    _loaded_models.append(model)


def generate_spec():  # pragma: no cover
    pass


def sync_spec():  # pragma: no cover
    pass


def pop_execute_query_kwargs(keyword_arguments):
    """ pop the optional execute query arguments from arbitrary kwargs;
        return non-None query kwargs in a dict
    """
    query_kwargs = {}
    for key in ('graph_name', 'traversal_source', 'pool'):
        val = keyword_arguments.pop(key, None)
        if val is not None:
            query_kwargs[key] = val
    return query_kwargs
