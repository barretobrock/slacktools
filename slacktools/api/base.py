from typing import Dict


class BaseApiObject:
    """The base of the event classes"""

    def __init__(self, resp_dict: Dict = None, **kwargs):
        if resp_dict is not None:
            self._dict_to_props(resp_dict)
        self._dict_to_props(kwargs)

    def _dict_to_props(self, resp_dict: Dict):
        for k, v in resp_dict.items():
            if isinstance(v, dict):
                self.__setattr__(k, BaseApiObject(v))
            elif isinstance(v, list):
                self.__setattr__(k, [BaseApiObject(x) if isinstance(x, dict) else x for x in v])
            else:
                self.__setattr__(k, v)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'


class ResponseMetadata(BaseApiObject):
    next_cursor: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'
