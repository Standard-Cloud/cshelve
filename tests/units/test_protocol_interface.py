"""
The `open` function accept a `protocol` argument but the `cshelve` module do not interract with it.
The impact is on the algorithm used by the `Shelf` object and not directly on `cshelve`.
Anyway, the library must support it.
"""
import pickle
from unittest.mock import Mock

import cshelve
from cshelve._parser import Config, ProviderConfig


def test_use_protocol():
    """
    Provide the protocol argument and check if it is passed to the shelve module.
    """
    filename = "test.ini"
    provider = "myprovider"
    protocol = pickle.HIGHEST_PROTOCOL
    config = {
        "provider": provider,
        "auth_type": "passwordless",
        "container_name": "mycontainer",
    }

    cdit = Mock()
    factory = Mock()
    loader = Mock()

    factory.return_value = cdit

    provider_config = ProviderConfig(
        provider=provider,
        use_versionning=True,
        default=config,
        logging={},
        compression={},
        encryption={},
        provider_params={},
    )

    loader.return_value = Config(
        providers=[provider_config],
        provider_routing="all",
        use_pickle=True,
    )

    # Replace the default parser with the mock parser.
    db = cshelve.open(
        filename, protocol=protocol, config_loader=loader, factory=factory
    )

    assert db._protocol == protocol
