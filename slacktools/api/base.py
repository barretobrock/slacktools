from typing import Dict


def dict_to_props(obj, event_dict):
    for key, value in event_dict.items():
        if isinstance(value, dict):
            setattr(obj, key, dict_to_props(obj, value))
        else:
            setattr(obj, key, value)
    return obj


class SubItemApiObject:
    def __getattr__(self, item):
        return None


class BaseApiObject:
    """The base of the event classes"""

    def __init__(self, event_dict: Dict):
        for k, v in event_dict.items():
            if isinstance(v, dict):
                subitem = dict_to_props(SubItemApiObject(), v)
                self.__setattr__(k, subitem)
            else:
                self.__setattr__(k, v)

    def __getattr__(self, item):
        return None
