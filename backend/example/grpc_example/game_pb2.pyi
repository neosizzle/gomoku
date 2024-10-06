from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AI_STANDARD: _ClassVar[ModeType]
    AI_PRO: _ClassVar[ModeType]
    PVP_STANDARD: _ClassVar[ModeType]
    PVP_PRO: _ClassVar[ModeType]
AI_STANDARD: ModeType
AI_PRO: ModeType
PVP_STANDARD: ModeType
PVP_PRO: ModeType

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GameMeta(_message.Message):
    __slots__ = ("_initialized", "gameId", "mode", "gridSize")
    _INITIALIZED_FIELD_NUMBER: _ClassVar[int]
    GAMEID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    GRIDSIZE_FIELD_NUMBER: _ClassVar[int]
    _initialized: bool
    gameId: int
    mode: ModeType
    gridSize: int
    def __init__(self, _initialized: bool = ..., gameId: _Optional[int] = ..., mode: _Optional[_Union[ModeType, str]] = ..., gridSize: _Optional[int] = ...) -> None: ...

class GameState(_message.Message):
    __slots__ = ("board", "p1_captures", "p0_captures", "num_turns", "is_end")
    BOARD_FIELD_NUMBER: _ClassVar[int]
    P1_CAPTURES_FIELD_NUMBER: _ClassVar[int]
    P0_CAPTURES_FIELD_NUMBER: _ClassVar[int]
    NUM_TURNS_FIELD_NUMBER: _ClassVar[int]
    IS_END_FIELD_NUMBER: _ClassVar[int]
    board: bytes
    p1_captures: int
    p0_captures: int
    num_turns: int
    is_end: bool
    def __init__(self, board: _Optional[bytes] = ..., p1_captures: _Optional[int] = ..., p0_captures: _Optional[int] = ..., num_turns: _Optional[int] = ..., is_end: bool = ...) -> None: ...
