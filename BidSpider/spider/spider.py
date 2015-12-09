import asyncio
from abc import ABCMeta, abstractmethod, abstractproperty
from spider.item import Item


class Spider(metaclass=ABCMeta):

    @abstractmethod
    @asyncio.coroutine
    def parse(self, response):
        return Item()

    @abstractproperty
    def name(self):
        return self.name

    @abstractproperty
    def domain(self):
        return self.domain

