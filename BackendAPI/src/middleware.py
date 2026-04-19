from uuid import uuid4
from starlette.requests import cookie_parser
from starlette.types import ASGIApp, Receive, Scope, Send

from starlette.datastructures import Headers, MutableHeaders


def get_cookies(scope: Scope) -> dict[str, str]:
    request_headers = Headers(scope=scope)
    cookie_header = request_headers.get('cookie', default="")

    return cookie_parser(cookie_header)


class SessionIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def append_session_cookie():
            message = await receive()
            print(message)
            return message

        async def send_with_extra_headers(message):
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                
                cookies = get_cookies(scope)
                session_id = cookies.get('session_id') or str(uuid4())
                response_headers.append('Set-Cookie', f'session_id={session_id}; Path=/')
                scope.setdefault('state', {})['session_id'] = session_id
                scope['session_id'] = session_id

            await send(message)

        await self.app(scope, append_session_cookie, send_with_extra_headers)
