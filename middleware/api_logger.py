from starlette.requests import Request
from starlette.types import Send, Receive, Scope, ASGIApp

from controller.es_retriever import add_api_logs_to_es_middleware


class ESAPILogger:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.app(scope, receive, send)
        client = scope["client"]
        request = Request(scope, receive)
        if "tenant-id" in request.headers:
            tenant_id = request.headers['tenant-id']
            add_api_logs_to_es_middleware(request, tenant_id, client)