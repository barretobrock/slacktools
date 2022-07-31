from typing import (
    Dict,
    List,
    TypedDict,
    Union,
)


class BaseEventType(TypedDict):
    type: str


class StandardMessageEventType(BaseEventType):
    channel: str
    user: str
    text: str
    ts: str


class ThreadedMessageEventType(StandardMessageEventType, total=False):
    message: StandardMessageEventType
    subtype: str    # message_replied
    thread_ts: str


AllMessageEventTypes = Union[StandardMessageEventType, ThreadedMessageEventType]


class ChannelDataType(TypedDict):
    id: str
    name: str
    created: int
    creator: str


class ChannelCreatedEventType(BaseEventType):
    channel: ChannelDataType


class _EmojiChangedEventType(BaseEventType):
    subtype: str
    event_ts: str


class EmojiAddedEventType(_EmojiChangedEventType):
    value: str


class EmojiRenamedEventType(_EmojiChangedEventType):
    old_name: str
    new_name: str
    value: str


class EmojiRemovedEventType(_EmojiChangedEventType):
    names: List[str]


EmojiChangedEvents = Union[EmojiAddedEventType, EmojiRenamedEventType, EmojiRemovedEventType]


class EventItemType(BaseEventType, total=False):
    channel: str
    ts: str


class ReactionEventType(BaseEventType):
    user: str
    reaction: str
    item_user: str
    item: EventItemType
    event_ts: str


class PinEventType(BaseEventType):
    user: str
    channel_id: str
    item: EventItemType
    has_pins: bool
    event_ts: str


class UserProfileType(TypedDict):
    title: str
    phone: str
    skype: str
    real_name: str
    real_name_normalized: str
    display_name: str
    display_name_normalized: str
    fields: Dict
    status_text: str
    status_emoji: str
    status_emoji_display_info: str
    status_expiration: str
    avatar_hash: str
    first_name: str
    last_name: str
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    status_text_canonical: str
    team: str


class UserInfoType(TypedDict):
    id: str
    team_id: str
    name: str
    deleted: bool
    color: str
    real_name: str
    tz: str
    tz_label: str
    tz_offset: int
    profile: UserProfileType
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_bot: bool
    is_app_user: bool
    updated: int
    is_email_confirmed: bool
    who_can_share_contact_card: str
    locale: str


class UserChangeType(BaseEventType):
    user: UserInfoType
    event_ts: str
    cache_ts: int


ALL_EVENTS = Union[
    ChannelCreatedEventType,
    EmojiAddedEventType,
    EmojiRemovedEventType,
    EmojiRenamedEventType,
    PinEventType,
    ReactionEventType,
    StandardMessageEventType,
    UserChangeType
]


class EventWrapperType(TypedDict, total=False):
    """This is the dict that includes the event"""
    event: ALL_EVENTS
