import atexit
from time import sleep
from typing import Optional

from testcontainers.core.generic import DockerContainer  # type: ignore
import requests.exceptions

from loguru import logger

from pytezos.sandbox.node import SandboxedNodeTestCase
from pytezos.sandbox.parameters import sandbox_addresses, sandbox_commitment

from pytezos.client import PyTezosClient
from pytezos.operation.group import OperationGroup
from pytezos.sandbox.parameters import FLORENCE

from src.deploy import deploy_market, deploy_stablecoin
from src.market import Market
from src.stablecoin import Stablecoin

# NOTE: Container object is a singleton which will be used in all tests inherited from class _SandboxedNodeTestCase
# and stopped after all tests are completed.
node_container: Optional[DockerContainer] = None
node_container_client: PyTezosClient = PyTezosClient()
node_fitness: int = 1


class SandboxedTestCase(SandboxedNodeTestCase):

    PORT: Optional[int] = 20000

    @classmethod
    def setUpClass(cls) -> None:
        """Spin up sandboxed node container and activate protocol."""
        global node_container  # pylint: disable=global-statement
        if not node_container:
            node_container = cls._create_node_container()
            node_container.start()
            cls._wait_for_connection()
            atexit.register(node_container.stop)

        cls.activate(cls.PROTOCOL, reset=True)
        id = deploy_market(key="bootstrap2")
        stablecoin = deploy_stablecoin()

    @classmethod
    def activate(cls, protocol_alias: str, reset: bool = False) -> OperationGroup:
        """Activate protocol."""
        return (
            cls.get_client()
            .using(key='dictator')
            .activate_protocol(protocol_alias)
            .fill(block_id='genesis' if reset else 'head')
            .sign()
            .inject()
        )

    @classmethod
    def get_node_url(cls) -> str:
        """Get sandboxed node URL."""
        container = cls._get_node_container()
        container_id = container.get_wrapped_container().id
        host = container.get_docker_client().bridge_ip(container_id)
        return f'http://{host}:20000'

    @classmethod
    def _get_node_container(cls) -> DockerContainer:
        if node_container is None:
            raise RuntimeError('Sandboxed node container is not running')
        return node_container

    @classmethod
    def get_client(cls) -> PyTezosClient:
        return node_container_client.using(
            shell=cls.get_node_url(),
        )

    @classmethod
    def _create_node_container(cls) -> DockerContainer:
        container = DockerContainer(
            cls.IMAGE,
        )
        if cls.PORT:
            container.ports[8732] = cls.PORT
        return container

    @classmethod
    def _wait_for_connection(cls) -> None:
        client = cls.get_client()
        logger.error(client)
        while True:
            try:
                client.shell.node.get("/version/")
                break
            except requests.exceptions.ConnectionError as e:
                logger.error(e)
                sleep(0.1)

    @classmethod
    def bake_block(cls, min_fee: int = 0) -> OperationGroup:
        """Bake new block.
        :param min_fee: minimum fee of operation to be included in block
        """
        return cls.get_client().using(key='bootstrap1').bake_block(min_fee).fill().work().sign().inject()

    @property
    def client(self) -> PyTezosClient:
        """PyTezos client to interact with sandboxed node."""
        return self.get_client().using(key='bootstrap2')