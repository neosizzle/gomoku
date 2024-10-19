# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: game.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'game.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ngame.proto\x1a\x1egoogle/protobuf/wrappers.proto\"#\n\x0bMoveRequest\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\"\x07\n\x05\x45mpty\"b\n\x08GameMeta\x12\x14\n\x0c_initialized\x18\x01 \x01(\x08\x12\x14\n\x0clast_updated\x18\x02 \x01(\x04\x12\x17\n\x04mode\x18\x03 \x01(\x0e\x32\t.ModeType\x12\x11\n\tgrid_size\x18\x04 \x01(\x04\"\x81\x01\n\tGameState\x12\r\n\x05\x62oard\x18\x01 \x01(\x0c\x12\x13\n\x0bp1_captures\x18\x02 \x01(\x04\x12\x13\n\x0bp0_captures\x18\x03 \x01(\x04\x12\x11\n\tnum_turns\x18\x04 \x01(\x04\x12\x0e\n\x06is_end\x18\x05 \x01(\x08\x12\x18\n\x10time_to_think_ns\x18\x06 \x01(\x04*F\n\x08ModeType\x12\x0f\n\x0b\x41I_STANDARD\x10\x00\x12\n\n\x06\x41I_PRO\x10\x01\x12\x10\n\x0cPVP_STANDARD\x10\x02\x12\x0b\n\x07PVP_PRO\x10\x03\x32\xf8\x01\n\x04Game\x12\"\n\x0bGetGameMeta\x12\x06.Empty\x1a\t.GameMeta\"\x00\x12\"\n\x0bSetGameMeta\x12\t.GameMeta\x1a\x06.Empty\"\x00\x12\x19\n\x05Reset\x12\x06.Empty\x1a\x06.Empty\"\x00\x12+\n\x0fSuggestNextMove\x12\n.GameState\x1a\n.GameState\"\x00\x12(\n\x10GetLastGameState\x12\x06.Empty\x1a\n.GameState\"\x00\x12\x36\n\nPlacePiece\x12\x0c.MoveRequest\x1a\x1a.google.protobuf.BoolValueb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'game_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MODETYPE']._serialized_start=324
  _globals['_MODETYPE']._serialized_end=394
  _globals['_MOVEREQUEST']._serialized_start=46
  _globals['_MOVEREQUEST']._serialized_end=81
  _globals['_EMPTY']._serialized_start=83
  _globals['_EMPTY']._serialized_end=90
  _globals['_GAMEMETA']._serialized_start=92
  _globals['_GAMEMETA']._serialized_end=190
  _globals['_GAMESTATE']._serialized_start=193
  _globals['_GAMESTATE']._serialized_end=322
  _globals['_GAME']._serialized_start=397
  _globals['_GAME']._serialized_end=645
# @@protoc_insertion_point(module_scope)
