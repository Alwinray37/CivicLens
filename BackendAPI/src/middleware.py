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

        cookies = get_cookies(scope)
        session_id = cookies.get('session_id')
        had_session_id = True

        if session_id is None:
            had_session_id = False
            session_id = str(uuid4())

        async def set_session_id_cookie(message):
            if message["type"] == "http.response.start" and (not had_session_id):
                response_headers = MutableHeaders(scope=message)

                nonlocal session_id
                assert session_id is not None

                response_headers.append('Set-Cookie', f'session_id={session_id}; Path=/')

            await send(message)

        scope['session_id'] = session_id

        await self.app(scope, receive, set_session_id_cookie)
