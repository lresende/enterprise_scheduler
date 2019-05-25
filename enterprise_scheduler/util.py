# -*- coding: utf-8 -*-
#
# Copyright 2018-2019 Luciano Resende
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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

    print('> Processing resources from: ' + directory)
    for root, dirs, files in os.walk(directory):
        for file in files:
            print('> Adding file to job archive: ' + file)
            zip_file.write(os.path.join(root, file), file)

    zip_file.close()

