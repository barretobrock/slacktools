import random
import string
from typing import (
    Callable,
    Dict,
    List,
    Union,
)


class BlockKitBuilder:
    pass


class ExceededMaxLengthException(Exception):
    pass


class BaseElement:

    def __init__(self, **kwargs):
        for name, val in kwargs.items():
            self.__setattr__(name, val)

    def asdict(self) -> Dict:
        resp_dict = {}
        for k, v in vars(self).items():
            if k.startswith('_'):
                continue
            if isinstance(v, BaseElement):
                resp_dict[k] = v.asdict()
            elif isinstance(v, list):
                items = []
                for item in v:
                    if isinstance(item, BaseElement):
                        items.append(item.asdict())
                    else:
                        items.append(item)
                resp_dict[k] = items
            else:
                resp_dict[k] = v
        return resp_dict

    def __getattr__(self, item):
        # This helps to avoid getting AttributeError on values.
        #   Instead they'll just return None, which is the pattern
        #   we want to work with.
        return None

    @staticmethod
    def length_assertion(value: Union[str, List], key: str, max_len: int):
        value_len = len(value)
        if value_len > max_len:
            raise ExceededMaxLengthException(f'Key "{key}" exceeded the max length allowed: {value_len} / {max_len}')


def dictify_blocks(f) -> Callable:
    """
    This is meant to be used as a decorator on methods that return a list of blocks.
        The process iterates through the pre-formatted BaseElement-based objects and calls `.asdict()`
        to render them to dicts.
    """
    def inner(*args, **kwargs) -> List[Dict]:
        result = f(*args, **kwargs)

        if isinstance(result, list):
            processed = []
            for item in result:
                if isinstance(item, BaseElement):
                    processed.append(item.asdict())
                else:
                    processed.append(item)
            return processed
        else:
            return result
    return inner


BlocksType = List[Union[Dict, BaseElement]]


def random_string(n_chars: int = 10, addl_chars: str = None) -> str:
    """Generates a random string of n characters in length"""
    chars = string.ascii_letters
    if addl_chars is not None:
        chars += addl_chars
    return ''.join([random.choice(chars) for i in range(n_chars)])
