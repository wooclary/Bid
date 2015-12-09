from abc import ABCMeta, abstractclassmethod


class BasePipeline(metaclass=ABCMeta):
    @abstractclassmethod
    def process_item(self, item, spider):
        pass
