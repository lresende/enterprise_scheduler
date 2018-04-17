
import asyncio

def fix_asyncio_event_loop_policy(asyncio):
    """
    Work around https://github.com/tornadoweb/tornado/issues/2183
    """
    class PatchedDefaultEventLoopPolicy(asyncio.DefaultEventLoopPolicy):

        def get_event_loop(self):
            """Get the event loop.
            This may be None or an instance of EventLoop.
            """
            try:
                return super().get_event_loop()
            except RuntimeError:
                # "There is no current event loop in thread"
                loop = self.new_event_loop()
                self.set_event_loop(loop)
                return loop

    asyncio.set_event_loop_policy(PatchedDefaultEventLoopPolicy())


