import inspect
import importlib


def list_subclasses_in_specific_module(module_name, base_cls, tuple_with_cls_name=False):
    module = importlib.import_module(module_name)
    cls_members = inspect.getmembers(module, inspect.isclass)
    own_cls_members = \
        [m if tuple_with_cls_name else m[1] for m in cls_members
         if m[1].__module__ == module_name and issubclass(m[1], base_cls)]
    return own_cls_members


def import_a_name_from_a_module(module_dot_name):
    split_word = module_dot_name.split('.')
    name = split_word[-1]
    module = '.'.join(split_word[:-1])
    m = importlib.import_module(module)
    name = getattr(m, name)
    return name


if __name__ == '__main__':
    # print(list_sth_in_specific_module('spiders'))
    import_path = 'spider.spider.Spider'
    print(import_a_name_from_a_module(import_path))
