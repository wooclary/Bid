from base_error import ArgumentError, WrongArgumentType

"""
link_extractor模块相关错误
"""


class PageRangeUndefined(ArgumentError):
    def __init__(self):
        super().__init__('start or end cannot be None')


class PageRangeTypeError(WrongArgumentType):
    def __init__(self):
        super().__init__('start or end must be int type')
