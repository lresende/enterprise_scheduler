import os
import asyncio
import zipfile


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

def zip_directory(zip_name, directory):
    zip_file = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(directory):
        for file in files:
            zip_file.write(os.path.join(root, file), file)

    zip_file.close()

