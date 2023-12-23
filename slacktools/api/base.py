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

    def asdict(self) -> Dict:
        resp_dict = {}
        for k, v in vars(self).items():
            if k.startswith('_'):
                continue
            if isinstance(v, BaseApiObject):
                resp_dict[k] = v.asdict()
            elif isinstance(v, list):
                items = []
                for item in v:
                    if isinstance(item, BaseApiObject):
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

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'


class ResponseMetadata(BaseApiObject):
    next_cursor: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'
