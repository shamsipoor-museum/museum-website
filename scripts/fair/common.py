from typing import Union, Collection

import global_values as gv
FA_IR_PREFIX = gv.PREFIX + "fa_IR/"


def persian_stringifier(c: Union[None, str, Collection[str]]) -> str:
    """stringify a collection of strings using persian commas if it's not a string already
    if c is None; "-" will be returned"""
    return "-" if c is None else c if isinstance(c, str) else "، ".join(c)
