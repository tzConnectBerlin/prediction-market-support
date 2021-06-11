from typing import Optional

from testcontainers.core.generic import DockerContainer  # type: ignore

from pytezos.sandbox.node import SandboxedNodeTestCase
from pytezos.sandbox.parameters import sandbox_addresses, sandbox_commitment


class SandboxedTestCase(SandboxedNodeTestCase):

    PORT: Optional[int] = 20000

    @classmethod
    def get_node_url(cls) -> str:
        """Get sandboxed node URL."""
        container = cls._get_node_container()
        container_id = container.get_wrapped_container().id
        host = container.get_docker_client().bridge_ip(container_id)
        return f'http://{host}:20000'

    @classmethod
    def _create_node_container(cls) -> DockerContainer:
        container = DockerContainer(
            cls.IMAGE,
        )
        if cls.PORT:
            container.ports[8732] = cls.PORT
        return container
