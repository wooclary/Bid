from collections import MutableMapping
from abc import ABCMeta
import importlib
import json


class Field(object):
    """Item的字段对象"""
    pass


class ItemMeta(ABCMeta):
    """Item的元类，用于改变声明class的API"""

    def __new__(mcs, cls_name, bases, attrs):
        if cls_name == 'Item':
            super(ItemMeta, mcs).__new__(mcs, cls_name, bases, attrs)

        fields = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields[k] = v

        for k in fields:
            attrs.pop(k)

        attrs['fields'] = fields
        return super(ItemMeta, mcs).__new__(mcs, cls_name, bases, attrs)


class DictItem(MutableMapping):
    """
    Item的基类，用于构造Item的API
    继承了MutableMapping接口，使之用起来更像dict
    """

    fields = {}

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args or kwargs:  # 避免重复创建value dict
            for k, v in dict(*args, **kwargs).items():
                self[k] = v

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value
        else:
            raise KeyError('%s 没有定义字段: %s' % (self.__class__.__name__, key))

    def __delitem__(self, key):
        del self._values[key]

    def __getattr__(self, name):
        if name in self.fields:
            raise AttributeError("请使用 item[%r] 来获得字段值" % name)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            raise AttributeError("请使用 item[%r] = %r 来设置字段值" % (name, value))
        super(DictItem, self).__setattr__(name, value)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def keys(self):
        return self._values.keys()

    def copy(self):
        return self.__class__(self)

    def __contains__(self, key):
        return key in self._values

    def __str__(self):
        return self._values.__str__()

    def get_dict(self):
        return self._values


class Item(DictItem, metaclass=ItemMeta):
    """所有具体的Item类由此派生"""
    pass


def item2dict(item):
    """
    将 class spider.item.Item 的实例转化成python dict
    用于 class spider.item.Item 的json序列化
    """
    d = item.get_dict()
    d['__class__'] = item.__class__.__name__
    d['__module__'] = item.__module__
    return d


def dict2item(d):
    """
    将 python dict 转化成 class spider.item.Item 的实例
    用于 class spider.item.Item 的反json序列化
    """
    if'__class__' in d:
        # 获取class和module的名称
        class_name = d.pop('__class__')
        module_name = d.pop('__module__')

        # 导入module
        module = importlib.import_module(module_name)

        # 根据module获取class类对象
        class_ = getattr(module, class_name)

        # 使用class类对象创建实例
        inst = class_(d)
    else:
        inst = d
    return inst


def items2jsonarray(items):
    return json.dumps([item2dict(item) for item in items])


def jsonarray2items(json_array):
    return [dict2item(d) for d in json.loads(json_array)]

