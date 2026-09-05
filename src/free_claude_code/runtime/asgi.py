import asyncio

from loguru import logger
from starlette.types import ASGIApp, Receive, Scope, Send

from .application import ApplicationRuntime, startup_failure_message


class RuntimeASGIApp:
    """Delegate HTTP to FastAPI and lifespan to `ApplicationRuntime`."""

    def __init__(self, app: ASGIApp, runtime: ApplicationRuntime) -> None:
        self.app = app
        self.runtime = runtime
        self._startup_lock = asyncio.Lock()

    def __getattr__(self, name: str) -> object:
        """Expose the wrapped application's public interface transparently."""
        return getattr(self.app, name)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "lifespan":
            if not self.runtime._started:
                async with self._startup_lock:
                    if not self.runtime._started:
                        await self.runtime.start()
            await self.app(scope, receive, send)
            return
        await self._lifespan(receive, send)

    async def _lifespan(self, receive: Receive, send: Send) -> None:
        started = False
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    await self.runtime.start()
                except Exception as exc:
                    await send(
                        {
                            "type": "lifespan.startup.failed",
                            "message": startup_failure_message(
                                self.runtime.settings,
                                exc,
                            ),
                        }
                    )
                    return
                started = True
                await send({"type": "lifespan.startup.complete"})
                continue

            if message["type"] == "lifespan.shutdown":
                if started:
                    try:
                        closed = await self.runtime.close()
                    except Exception as exc:
                        logger.error(
                            "Shutdown failed: exc_type={}",
                            type(exc).__name__,
                        )
                        await send({"type": "lifespan.shutdown.failed", "message": ""})
                        return
                    if not closed:
                        await send({"type": "lifespan.shutdown.failed", "message": ""})
                        return
                await send({"type": "lifespan.shutdown.complete"})
                return
