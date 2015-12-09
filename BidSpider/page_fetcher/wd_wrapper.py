import asyncio
from selenium import webdriver
from time import sleep
from page_fetcher.req_and_res import Response


class WebDriver(object):
    def __init__(self, i, log_path):
        service_args = [
            '--ignore-ssl-errors=true',
            '--load-images=false',
            '--disk-cache=true'
        ]

        self.id = i
        self.driver = \
            webdriver.PhantomJS(service_args=service_args,
                                service_log_path=
                                None if log_path is None else(log_path + 'ghostdriver{}.log'.format(i)))
        self.driver.set_window_size(1120, 550)

    def get(self, req):
        url = req.url
        self.driver.get(url)
        sleep(1)
        whole_page = self.driver.find_element_by_tag_name('html').get_attribute('outerHTML')
        return Response(url, whole_page)

    def close(self):
        self.driver.close()


class WDManagerWithSemaphore(object):
    """
    WebDriver的管理类，信号灯实现

    重用WebDriver提高效率
    """
    def __init__(self, size, log_path=None):
        self.free_list = [WebDriver(i+1, log_path) for i in range(size)]
        self.semaphore = asyncio.Semaphore(size)

    @asyncio.coroutine
    def acquire_idle_webdriver(self):
        """
        获取空闲的WebDriver

        获取semaphore的操作是由函数调用实现的，需要使用协程
        """
        yield from self.semaphore.acquire()
        wd = self.free_list.pop()
        return wd

    def recycle_idle_webdriver(self, wd):
        """
        回收空闲的WebDriver

        释放semaphore的操作是由函数调用实现的，不需要使用协程
        """
        self.free_list.insert(0, wd)
        self.semaphore.release()
        return

    def release(self):
        """
        释放Manager的所有WebDriver
        """
        for wd in self.free_list:
            wd.close()


if __name__ == '__main__':
    pass
