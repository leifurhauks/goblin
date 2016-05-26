from goblin import connection
# TODO: maybe a setting "CLIENT" (e.g. aiohttp, tornado) that takes care of pool_class etc?
_config = None


def get_global_config():
    if _config is None:
        raise Exception("You must first call goblin.config.setup")
    return _config


_default_settings = {
    "GRAPH_NAME": "graph",
    "TRAVERSAL_SOURCE": "g",
    "USERNAME": "",
    "PASSWORD": "",
    "POOL_SIZE": 256,
    "SSL_CONTEXT": None,
}

required_settings = ("URL", "POOL_CLASS", "FUTURE_CLASS",)


def _assert_required_settings(user_settings):
    user_keys = frozenset(user_settings.keys())
    missing_required = frozenset(required_settings) - user_keys
    if len(missing_required) > 0:
        raise AssertionError("Missing required setting(s): {}"
                             .format(tuple(missing_required)))


def setup(user_settings, loop=None):
    """
    Initialize the connection pool and the global configuration dictionary.
    :param user_settings:  Dictionary of configuration values
    :type user_settings: dict
    """
    _assert_required_settings(user_settings)

    settings_dict = _default_settings.copy()
    settings_dict.update(user_settings)

    connection.setup(
        url=settings_dict["URL"],
        pool_class=settings_dict["POOL_CLASS"],
        graph_name=settings_dict["GRAPH_NAME"],
        traversal_source=settings_dict["TRAVERSAL_SOURCE"],
        username=settings_dict["USERNAME"],
        password=settings_dict["PASSWORD"],
        pool_size=settings_dict["POOL_SIZE"],
        future_class=settings_dict["FUTURE_CLASS"],
        ssl_context=settings_dict["SSL_CONTEXT"],
        loop=loop
    )

    global _config
    _config = settings_dict
