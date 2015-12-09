from abc import ABCMeta, abstractclassmethod
from link_extractor.error import *


class BaseLinkExtractor(metaclass=ABCMeta):
    """
    LinkExtractor基类，必须实现子类
    只需实例化一次，会多次调用extract_link方法
    """
    @abstractclassmethod
    def extract_link(self, response):
        """
        从response中提取link

        :param response
        通过response.text获取内容，response.url获取url
        """
        pass


class BaseLinks(metaclass=ABCMeta):
    @abstractclassmethod
    def extract_link(self):
        """"""
        pass


class PageNumIncrementLinks(BaseLinks):
    """
    针对pager的一次性计算所有页面链接的LinkExtractor
    """
    def __init__(self, start, end, format_str):
        """初始化

        :param format_str
        表示页码链接格式的字符串，使用占位符'{PageNum}'替换url的页码部分，
        格式字符串中有且只有一个占位符。
        """
        # TODO 使用参数validator实现参数检查
        if start is None or end is None:
            raise PageRangeUndefined()
        elif not (isinstance(start, int) and isinstance(end, int)):
            raise PageRangeTypeError()
        # TODO 对format_str进行语法检查

        self._end = end
        self._current = start

        format_str = format_str.split('{PageNum}')
        self._get_num_link = \
            lambda page_num: format_str[0] + str(page_num) + format_str[1]

    def extract_link(self):
        while self._current <= self._end:
            link = self._get_num_link(self._current)
            self._current += 1
            yield link
        return


if __name__ == '__main__':
    pass
