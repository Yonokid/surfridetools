import os
import struct
from enum import IntEnum
from io import BytesIO

from bidict import bidict

from save_json import NoIndent


class PropertyType(IntEnum):
    None_ = 0x00  # 0 bytes
    Bool = 0x01
    AnsiString = 0x02  # n bytes
    Char = 0x03
    UChar = 0x04
    Short = 0x05
    UShort = 0x06
    ShortAngle = 0x07
    Long = 0x08
    ULong = 0x09
    Float = 0x0A
    Angle = 0x0B
    ARGB8888 = 0x0C
    Double = 0x0D
    ArraySeparator = 0x0E  # 0 bytes

    IllegalType = 0x0F

SRD_DICT = bidict({
    0x00: ("SceneCount", PropertyType.UShort),
    0x01: ("TexListCount", PropertyType.UShort),
    0x03: ("Name", PropertyType.AnsiString),
    0x04: ("BackColor", PropertyType.ARGB8888),
    0x05: ("FontCount", PropertyType.UShort),
    0x06: ("CommentLength", PropertyType.Short),
    0x0E: ("AttributeCount", PropertyType.UShort),
    0x10: ("LayerCount", PropertyType.UShort),
    0x11: ("CameraCount", PropertyType.UShort),
    0x12: ("PositionXYZ", PropertyType.Float),
    0x13: ("TargetXYZ", PropertyType.Float),
    0x14: ("FovY", PropertyType.Angle),
    0x15: ("ZNear", PropertyType.Float),
    0x16: ("ZFar", PropertyType.Float),
    0x20: ("Flags", PropertyType.ULong),
    0x21: ("CastCount", PropertyType.UShort),
    0x22: ("AnimationCount", PropertyType.UShort),
    0x30: ("Flags2", PropertyType.ULong),
    0x31: ("TranslationXY", PropertyType.Float),
    0x32: ("RotationZ", PropertyType.Angle),
    0x33: ("Scale", PropertyType.Float),
    0x37: ("MaterialColorRGBA", PropertyType.ARGB8888),
    0x38: ("IlluminationColorRGBA", PropertyType.ARGB8888),
    0x39: ("VertexColorRGBA", PropertyType.ARGB8888),
    0x3A: ("Display", PropertyType.Bool),
    0x3B: ("Child", PropertyType.Short),
    0x3C: ("Sibling", PropertyType.Short),
    0x3D: ("MultiPosFlags", PropertyType.UShort),
    0x3E: ("MultiSizeFlags", PropertyType.UShort),
    0x40: ("Width", PropertyType.UShort),
    0x41: ("Height", PropertyType.UShort),
    0x42: ("PivotX", PropertyType.Float),
    0x43: ("PivotY", PropertyType.Float),
    0x44: ("CropRefCount", PropertyType.UShort),
    0x45: ("CropIndex", PropertyType.Short),
    0x48: ("ImageCastFlags", PropertyType.ULong),
    0x49: ("CropRef", PropertyType.Short),
    0x50: ("MotionCount", PropertyType.UShort),
    0x51: ("CastIndex", PropertyType.UShort),
    0x52: ("TrackCount", PropertyType.UShort),
    0x53: ("TrackType", PropertyType.UShort),
    0x54: ("Flags3", PropertyType.ULong),
    0x55: ("StartFrame", PropertyType.Long),
    0x56: ("EndFrame", PropertyType.Long),
    0x57: ("KeyCount", PropertyType.UShort),
    0x58: ("FirstFrame", PropertyType.Long),
    0x59: ("LastFrame", PropertyType.Long),
    0x5A: ("KeyFrame", PropertyType.Long),
    0x5B: ("KeyValue", PropertyType.Long),
    0x5C: ("Interpolation", PropertyType.UShort),
    0x5D: ("InParam", PropertyType.Float),
    0x5E: ("OutParam", PropertyType.Float),
    0x60: ("LayerCount2", PropertyType.UShort),
    0x61: ("TextureFileName", PropertyType.AnsiString),
    0x62: ("TextureFlags", PropertyType.ULong),
    0x63: ("CropCount", PropertyType.UShort),
    0x65: ("Rectangle", PropertyType.Short),
})

CHILD_MAPPING = bidict({
    "SRCK": "SurfBoard",
    "PROJ": "Project",
    "SCN ": "Scene",
    "TEX ": "Texture",
    "TEXL": "TexList",
    "CROP": "Crop",
    "CAM ": "Camera",
    "FONT": "Font",
    "CHAR": "Character",
    "LAYR": "Layer",
    "CAST": "Cast",
    "ANIM": "Animation",
    "MOT ": "Motion",
    "TRK ": "Track",
    "KEY ": "Key",
    "CIMG": "CropImage",
    "CREF": "CropR",
    "TRS2": "Transform2D",
    "TRS3": "Transform3D",
    "NODE": "Node",
    "DATA": "CastData",
    "NCAT": "NodeCast",
})
DATA_MAP = {
    PropertyType.Bool: '?',
    PropertyType.Short: 'h',
    PropertyType.UShort: 'H',
    PropertyType.Long: 'i',
    PropertyType.ULong: 'I',
    PropertyType.Float: 'f',
    PropertyType.Double: 'd',
    PropertyType.ARGB8888: '4B',
    PropertyType.Angle: 'I',
    PropertyType.AnsiString: 'string',
}

def bytes_to_hex(byte_string: bytes) -> str:
    return ''.join(f'\\x{byte:02x}' for byte in byte_string)

def validate_bytes(bytes_data: bytes, valid_data: bytes) -> bytes:
    if bytes_data != valid_data:
        raise Exception(f"Mismatched byte header: {bytes_to_hex(bytes_data)}, {bytes_to_hex(valid_data)}")
    return bytes_data

def read_vtbf(file: str) -> list[bytes]:
    chunks = []
    file_size = os.path.getsize(file)
    with open(file, 'rb') as f:
        _magic = validate_bytes(f.read(8), b'\x56\x54\x42\x46\x10\x00\x00\x00') #VTBF
        _type = f.read(4)
        _unknown = validate_bytes(f.read(4), b'\x01\x00\x00\x4c')
        while f.tell() != file_size:
            _header = validate_bytes(f.read(4), b'\x76\x74\x63\x30')
            chunk_size = struct.unpack("<I", f.read(4))[0]
            chunk = f.read(chunk_size)
            chunks.append(chunk)
    return chunks

def write_vtbf(output_file: str, chunks: list[bytes], type: str) -> None:
    with open(output_file, 'wb') as f:
        f.write(b'\x56\x54\x42\x46\x10\x00\x00\x00') #VTBF
        f.write(type.encode('utf-8'))
        f.write(b'\x01\x00\x00\x4c')
        for chunk in chunks:
            f.write(b'\x76\x74\x63\x30')
            f.write(struct.pack("<I", len(chunk)))
            f.write(chunk)

def read_property(format: str, file: BytesIO):
    if format == 'string':
        string_size = int.from_bytes(file.read(1))
        value = file.read(string_size).decode('utf-8')
    elif len(format) > 1:
        value = NoIndent(struct.unpack(format, file.read(struct.calcsize(format))))
    else:
        value = struct.unpack(format, file.read(struct.calcsize(format)))[0]
    return value

def read_property_type(f: BytesIO) -> str:
    type_byte = int.from_bytes(f.read(1))
    format = PropertyType(type_byte & 0x3F)
    has_dim1, has_dim2 = type_byte & 0x40, type_byte & 0x80
    if has_dim1 and has_dim2:
        raise Exception("Don't use this surfboard")
    if has_dim1:
        extra = int.from_bytes(f.read(1))
        return DATA_MAP[format] * (2 + extra)
    return DATA_MAP[format]

def read_properties(properties_len: int, file: BytesIO, type):
    property_dict = dict()
    for i in range(properties_len):
        srd_property = int.from_bytes(file.read(1))
        srd_property_type = read_property_type(file)
        property_name = SRD_DICT[srd_property][0]
        print(property_name)
        if property_name in property_dict:
            if not isinstance(property_dict[property_name], list):
                property_dict[property_name] = [property_dict[property_name]]
            property_dict[property_name].append(read_property(srd_property_type, file))
        else:
            property_dict[property_name] = read_property(srd_property_type, file)
    return property_dict

def build_tree_from_tuples(data):
    stack = []
    for i in range(len(data)):
        curr_node, curr_children, type = data[i]

        if not stack:
            stack.append([curr_node, curr_children, type])
        else:
            curr_child, num_children, curr_type = stack[-1]

            child_name = CHILD_MAPPING.get(type, type)
            if child_name not in curr_child:
                curr_child[child_name] = []
            if isinstance(curr_node, list):
                curr_child[child_name] = curr_node
            else:
                curr_child[child_name].append(curr_node)

            if num_children == 1:
                stack.pop()
            else:
                stack[-1][1] -= 1

            if curr_children > 0:
                stack.append([curr_node, curr_children, type])
    return data[0][0]

def build_tuples_from_tree(tree):
    result = []

    def traverse_tree(node, node_type=None):
        if not isinstance(node, dict):
            # Leaf node with no children
            result.append((node, 0, node_type or "DATA"))
            return

        # Count total children across all child types
        total_children = 0
        for child_type, children in node.items():
            if isinstance(children, list):
                total_children += len(children)

        # Create a copy of the node without its children
        node_data = {
            k: v
            for k, v in node.items()
            if k not in CHILD_MAPPING.inverse
        }

        # Add current node to result
        type_code = node_type or "SRCK"  # Default to SRCK for root
        result.append((node_data, total_children, type_code))

        # Process all child types and their nodes
        for child_type, children in node.items():
            type_code = CHILD_MAPPING.inverse.get(child_type, child_type)
            if isinstance(children, list) and child_type in CHILD_MAPPING.inverse:
                for child in children:
                    traverse_tree(child, type_code)


    traverse_tree(tree)
    return result

def unpack_surfboard(chunks: list[bytes]):
    """
    Unpack VTBF chunk bytes into a dictionary.

    Parameters
    ----------
    input_file : str
        The directory in which to search for the file.

    Returns
    -------
    dict

    Description
    -----------
    This function reads the binary representation of a .sbscene
    file and returns a formatted dictionary.
    .srd files are planned but not implemented.
    The file header must match a valid sbscene file to process
    the data.

    The function will crash bytes are not provided in valid VTBF structure

    Examples
    --------
    >>> unpack_surfboard(vtbf_chunks)
    """
    srd_list = []
    for chunk in chunks:
        srd_dict = dict()
        f = BytesIO(chunk)
        type = f.read(4).decode()
        children = struct.unpack("<H", f.read(2))[0]
        properties = struct.unpack("<H", f.read(2))[0]
        if type in {"NODE", "TRS2", "NCAT"}:
            start_marker = b'\xFC\x00'
            separator = b'\xFE\x00'
            end_marker = b'\xFD\x00'
            start_index = chunk.find(start_marker)
            end_index = chunk.find(end_marker)
            list_data = chunk[start_index + len(start_marker):end_index]
            items = list_data.split(separator)
            type_dict_list = []
            properties = int((properties - len(items) - 1) / len(items))
            for item in items:
                type_dict_list.append(read_properties(properties, BytesIO(item), type))
            srd_dict = type_dict_list
        else:
            srd_dict = read_properties(properties, f, type)
        srd_list.append([srd_dict, children, type])
    return build_tree_from_tuples(srd_list)

def get_dict_item(tuple_dict, element):
    for key_tuple, value in tuple_dict.inverse.items():
        if key_tuple[0] == element:
            return value, key_tuple[1]
    return 0, 0

def repack_surfboard(json_file, output):
    srd_list = build_tuples_from_tree(json_file)
    srd_chunks = []
    types_seen = set()
    node_chunk = b''
    node_added = False
    trs2_chunk = b''
    trs2_added = False
    ncat_chunk = b''
    ncat_added = False
    for chunk in srd_list:
        srd_chunk = b''
        data, num_children, type = chunk
        is_array = type in {'NODE', 'NCAT', "TRS2"}
        if is_array:
            if type not in types_seen:
                types_seen.add(type)
                srd_chunk += type.encode('utf-8')
                srd_chunk += struct.pack("<H", num_children)
                srd_chunk += struct.pack("<H", len(data))
                srd_chunk += b'\xFC\x00'
            for key, value in data.items():
                srd_property, property_type = get_dict_item(SRD_DICT, key)
                srd_chunk += int.to_bytes(srd_property)
                srd_chunk += int.to_bytes(property_type)
                if isinstance(value, str):
                    srd_chunk += int.to_bytes(len(value))
                    srd_chunk += value.encode('ansi')
                elif isinstance(value, list):
                    if isinstance(value[0], float):
                        srd_chunk = srd_chunk[:-1]
                        srd_chunk += int.to_bytes(property_type | 0x40)
                        srd_chunk += int.to_bytes(len(value) - 2)
                        for val in value:
                            srd_chunk += struct.pack('f', val)
                    elif isinstance(value[0], list):
                        srd_chunk = srd_chunk[:-2]
                        for val_list in value:
                            srd_chunk += int.to_bytes(srd_property)
                            srd_chunk += int.to_bytes(property_type)
                            for val in val_list:
                                srd_chunk += int.to_bytes(val)
                    else:
                        for val in value:
                            srd_chunk += int.to_bytes(val)
                else:
                    srd_chunk += struct.pack(DATA_MAP[PropertyType(property_type)], value)
            srd_chunk += b'\xFE\x00'
            if type == 'NODE':
                node_chunk += srd_chunk
            elif type == 'TRS2':
                trs2_chunk += srd_chunk
            elif type == 'NCAT':
                ncat_chunk += srd_chunk
        else:
            if node_chunk != b'' and not node_added:
                node_chunk = node_chunk[:-2]
                node_chunk += b'\xFD\x00'
                srd_chunks.append(node_chunk)
                node_added = True
            if trs2_chunk != b'' and not trs2_added:
                trs2_chunk = trs2_chunk[:-2]
                trs2_chunk += b'\xFD\x00'
                srd_chunks.append(trs2_chunk)
                trs2_added = True
            if ncat_chunk != b'' and not ncat_added:
                ncat_chunk = ncat_chunk[:-2]
                ncat_chunk += b'\xFD\x00'
                srd_chunks.append(ncat_chunk)
                ncat_added = True
            srd_chunk += type.encode('utf-8')
            srd_chunk += struct.pack("<H", num_children)
            srd_chunk += struct.pack("<H", len(data))
            for key, value in data.items():
                srd_property, property_type = get_dict_item(SRD_DICT, key)
                srd_chunk += int.to_bytes(srd_property)
                srd_chunk += int.to_bytes(property_type)
                if isinstance(value, str):
                    srd_chunk += int.to_bytes(len(value))
                    srd_chunk += value.encode('ansi')
                elif isinstance(value, list):
                    if all(isinstance(val, float) for val in value):
                        srd_chunk += int.to_bytes(len(value))
                        for val in value:
                            srd_chunk += struct.pack('f', val)
                    else:
                        if key in {'CropIndex', 'CropRefCount'}:
                            srd_chunk = srd_chunk[:-2]
                            for val in value:
                                srd_chunk += int.to_bytes(srd_property)
                                srd_chunk += int.to_bytes(property_type)
                                srd_chunk += struct.pack('H', val)
                        elif key == 'CropRef':
                            srd_chunk += int.to_bytes(len(value) - 2)
                            srd_chunk += int.to_bytes(value[0])
                            srd_chunk += int.to_bytes(value[0])
                            srd_chunk += struct.pack('H', value[1])
                            srd_chunk += struct.pack('H', value[2])
                        else:
                            for val in value:
                                srd_chunk += int.to_bytes(val)
                elif isinstance(value, float):
                    srd_chunk += struct.pack(DATA_MAP[PropertyType.Float], value)
                else:
                    srd_chunk += struct.pack(DATA_MAP[PropertyType(property_type)], value)
            srd_chunks.append(srd_chunk)
    write_vtbf(output, srd_chunks, 'SRFF')
