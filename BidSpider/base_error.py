
class ArgumentError(Exception):
    """参数错误基类"""
    pass


class ArgumentUndefine(ArgumentError):
    """参数未定义错误"""
    pass


class WrongArgumentType(ArgumentError):
    """参数类型错误"""
    pass
