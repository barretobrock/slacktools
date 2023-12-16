from typing import (
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

    @staticmethod
    def length_assertion(value: Union[str, List], key: str, max_len: int):
        value_len = len(value)
        if value_len > max_len:
            raise ExceededMaxLengthException(f'Key "{key}" exceeded the max length allowed: {value_len} / {max_len}')


def dictify_blocks(f):
    """
    This is meant to be used as a decorator on methods that return a list of blocks.
        The process iterates through the pre-formatted BaseElement-based objects and calls `.asdict()`
        to render them to dicts.
    """
    def inner(*args, **kwargs):
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
