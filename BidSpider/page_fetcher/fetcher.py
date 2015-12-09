import asyncio


class PageFetcher(object):
    def __init__(self, event_loop, executor, wd_manager):
        self.loop = event_loop
        self.executor = executor
        self.wd_manager = wd_manager

    @asyncio.coroutine
    def do_fetching(self, req):
        wd = yield from self.wd_manager.acquire_idle_webdriver()
        future = self.loop.run_in_executor(self.executor, wd.get, req)
        response = yield from future
        self.wd_manager.recycle_idle_webdriver(wd)
        return response


if __name__ == '__main__':
    pass


