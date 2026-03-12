from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .clahe_node import CLAHEPreprocess

WEB_DIRECTORY = "./js"


class CLAHEExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [CLAHEPreprocess]


async def comfy_entrypoint() -> CLAHEExtension:
    return CLAHEExtension()
