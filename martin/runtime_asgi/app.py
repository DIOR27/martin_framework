from __future__ import annotations

from typing import Callable

from martin.core.context import BuildContext
from martin.render_html.html_renderer import HtmlRenderer


class MartinApp:

    def __init__(self, router):
        self.router = router
        self.renderer = HtmlRenderer(pretty=True, inline_css=True)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        path = scope["path"]

        resolved = self.router.resolve(path)

        if not resolved:
            await self._send_response(send, 404, "Not Found")
            return

        page_cls, params = resolved

        page_instance = page_cls(**params)

        context = BuildContext(request=scope, route=path)

        result = self.renderer.render_document(page_instance, context)

        await self._send_response(send, 200, result.html)

    async def _send_response(self, send, status: int, body: str):
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [(b"content-type", b"text/html; charset=utf-8")],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": body.encode("utf-8"),
            }
        )
