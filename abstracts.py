from abc import ABC
from typing import Optional

from httpx import Client


class SiteClient(ABC):
    base_url: str

    def __init__(self, *args, **kwargs) -> None:
        self.client = Client(
            base_url=type(self).base_url,
            timeout=None,
        )

