from typing import (
    Dict,
    Optional,
)

from slacktools.api.actions.actions import Action
from slacktools.block_kit.base import (
    BaseElement,
    BlocksType,
)


class ActionForm:
    """Enables tracking of multiple elements of a single form across separate requests"""

    def __init__(self, form_id: str, user_id: str):
        self.form_id = form_id
        self.user_id = user_id
        self.action_id_prefix = f'AF-{self.form_id}-{self.user_id}'
        self.form_items = {}  # type: Dict[str, BaseElement] # action-id:
        self.resp_items = {}  # type: Dict[str, Action]
        self.is_complete = False  # This is checked every time an action item comes in.
        # When an item ending in '-submit' comes it, this is flipped.

    def add_form_items(self, items: BlocksType):
        """Intakes Action item, modifies its action_id to be prefixed with """
        for item in items:
            if 'action_id' in item.__dict__.keys():
                item.action_id = f'{self.action_id_prefix}-{item.action_id}'
                self.form_items[item.action_id] = item
                # TODO: Add default values here?

    def get_form_item(self, action_id: str) -> Optional[BaseElement]:
        return self.form_items.get(action_id)

    def add_resp_item(self, resp_item: Action):
        if resp_item.action_id.startswith(self.action_id_prefix):
            self.resp_items[resp_item.action_id] = resp_item
        self.is_complete = resp_item.action_id.endswith('-submit')
