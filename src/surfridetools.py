import os
import struct
from dataclasses import MISSING, dataclass, field
from io import BufferedReader
from typing import Any, List

from save_json import NoIndent


class Variable:
    def __init__(self, map: dict):
        self.input_map = map
        self.output_map = dict()

def metadata_field(default_val: Any, header_bytes: bytes, format: str, length: int = 0, factory = MISSING) -> Any:
    if isinstance(default_val, list) and factory is MISSING:
        return field(default_factory=lambda: default_val.copy(), metadata={"header": header_bytes, "format": format, "length": length})
    elif factory is not MISSING:
        return field(default_factory=factory, metadata={"header": header_bytes, "format": format, "length": length})
    else:
        return field(default=default_val, metadata={"header": header_bytes, "format": format, "length": length})

@dataclass
class PROJ:
    SceneCount: int = metadata_field(-1, b'\x00\x06', '<H')
    TexListCount: int = metadata_field(-1, b'\x01\x06', '<H')
    FontCount: int = metadata_field(-1, b'\x05\x06', '<H')
    StartFrame: int = metadata_field(-1, b'\x55\x08', '<I')
    EndFrame: int = metadata_field(-1, b'\x56\x08', '<I')

@dataclass
class SCN:
    Name: str = metadata_field("", b'\x03\x02', 'string')
    LayerCount: int = metadata_field(-1, b'\x10\x06', '<H')
    CameraCount: int = metadata_field(-1, b'\x11\x06', '<H')
    BackColor: tuple = metadata_field((-1, -1, -1, -1), b'\x04\x0C', '4B')
    Width: int = metadata_field(-1, b'\x40\x06', '<H')
    Height: int = metadata_field(-1, b'\x41\x06', '<H')

@dataclass
class LAYR:
    Name: str = metadata_field("", b'\x03\x02', 'string')
    Flags: int = metadata_field(-1, b'\x20\x09', '<I')
    CastCount: int = metadata_field(-1, b'\x21\x06', '<H')
    AnimationCount: int = metadata_field(-1, b'\x22\x06', '<H')

@dataclass
class NODE:
    Name: str = metadata_field("", b'\x03\x02', 'string')
    Flags: int = metadata_field(-1, b'\x30\x09', '<I')
    Child: int = metadata_field(-1, b'\x3B\x05', '<h')
    Sibling: int = metadata_field(-1, b'\x3C\x05', '<h')

@dataclass
class TRS2:
    TranslationXY: tuple = metadata_field((-1, -1), b'\x31\x4A\x00', '<ff')
    RotationZ: int = metadata_field(-1, b'\x32\x0B', '<I')
    Scale: tuple = metadata_field((-1, -1), b'\x33\x4A\x00', '<ff')
    Display: bool = metadata_field(False, b'\x3A\x01', '<?')
    MaterialColorRGBA: tuple = metadata_field((-1, -1, -1, -1), b'\x37\x0C', '4B')
    IlluminationColorRGBA: tuple = metadata_field((-1, -1, -1, -1), b'\x38\x0C', '4B')
    VertexColorRGBA: List[tuple] = metadata_field([], b'\x39\x0C', '4B', 4, lambda: [(-1, -1, -1, -1)])
    MultiPosFlags: int = metadata_field(-1, b'\x3D\x06', '<H')
    MultiSizeFlags: int = metadata_field(-1, b'\x3E\x06', '<H')

@dataclass
class CIMG:
    ImageCastFlags: int = metadata_field(-1, b'\x48\x09', '<I')
    CastIndex: int = metadata_field(-1, b'\x51\x06', '<H')
    Width: int = metadata_field(-1.0, b'\x40\x0A', '<f')
    Height: int = metadata_field(-1.0, b'\x41\x0A', '<f')
    PivotX: int = metadata_field(-1.0, b'\x42\x0A', '<f')
    PivotY: int = metadata_field(-1.0, b'\x43\x0A', '<f')
    CropIndex: List[int] = metadata_field([], b'\x45\x05', '<H', 2, factory=lambda: [(-1, -1, -1, -1)])
    CropRefCount: List[int] = metadata_field([], b'\x44\x06', '<H', 2, factory=lambda: [(-1, -1, -1, -1)])

@dataclass
class CREF:
    TextureListIndexOld: int = metadata_field(0, b'\x49\x45\01', 'B')
    TextureListIndexConvert: int = metadata_field(0, b'', 'B')
    TextureIndex: int = metadata_field(-1, b'', '<H')
    CropIndex: int = metadata_field(-1, b'', '<H')

@dataclass
class ANIM:
    MotionCount: int = metadata_field(-1, b'\x50\x06', '<H')
    Name: str = metadata_field('', b'\x03\x02', 'string')
    EndFrame: int = metadata_field(-1, b'\x56\x08', '<I')

@dataclass
class MOT:
    CastIndex: int = metadata_field(-1, b'\x51\x05', '<H')
    TrackCount: int = metadata_field(-1, b'\x52\x06', '<H')

@dataclass
class TRK:
    TrackType: int = metadata_field(-1, b'\x53\x06', '<H')
    KeyCount: int = metadata_field(-1, b'\x57\x06', '<H')
    Flags: int = metadata_field(-1, b'\x54\x09', '<I')
    FirstFrame: int = metadata_field(-1, b'\x58\x08', '<I')
    LastFrame: int = metadata_field(-1, b'\x59\x08', '<I')

@dataclass
class KEY:
    KeyFrame: int = metadata_field(-1, b'\x5A\x08', '<I')
    KeyData: Variable = Variable({
                    347: ("KeyValue", "B"),
                    1628: ("Interpolation", "<H"),
                    2139: ("KeyValue", "<I"),
                    2651: ("KeyValue", "<f"),
                    2653: ("InParam", "<I"),
                    2654: ("OutParam", "<I"),
                    2907: ("KeyValue", "<i"),
                    3163: ("KeyValue_Color_RGBA", "4B"),
                })

@dataclass
class TEXL:
    Name: str = metadata_field('', b'\x03\x02', 'string')
    LayerCount: int = metadata_field(-1, b'\x60\x06', '<H')

@dataclass
class TEX:
    TextureFlags: int = metadata_field(-1, b'\x62\x09', '<I')
    TextureFileName: str = metadata_field('', b'\x61\x02', 'string')
    Width: int = metadata_field(-1, b'\x40\x06', '<H')
    Height: int = metadata_field(-1, b'\x41\x06', '<H')
    CropCount: int = metadata_field(-1, b'\x63\x06', '<H')

@dataclass
class CROP:
    Rectangle: tuple = metadata_field((-1, -1, -1, -1), b'\x65\x45\x02', '<HHHH')

@dataclass
class CAM:
    Name: str = metadata_field('', b'\x03\x02', 'string')
    PositionXYZ: tuple = metadata_field((-1, -1, -1), b'\x12\x4A\x01', '<fff')
    TargetXYZ: tuple = metadata_field((-1, -1, -1), b'\x13\x4A\x01', '<fff')
    FovY: int = metadata_field(-1, b'\x14\x0B', '<I')
    ZNear: int = metadata_field(-1, b'\x15\x0A', '<f')
    ZFar: int = metadata_field(-1, b'\x16\x0A', '<f')

class ChunkProcessor:
    def __init__(self):
        self.json_dict = dict()
        self.current_scene = dict()
        self.current_layer = dict()
        self.current_data = dict()
        self.current_cimg = dict()
        self.crop_ref_count = -1
        self.current_anim = dict()
        self.current_motion = dict()
        self.current_trk = dict()
        self.current_texl = dict()
        self.current_tex = dict()

    def get_dict(self):
        return self.json_dict

    def process_PROJ(self, file: BufferedReader, chunk_size: int) -> None:
        data = process_fields(file, PROJ())
        data["Scene"] = []
        self.json_dict = {"Project": data}

    def process_SCN(self, file: BufferedReader, chunk_size: int) -> None:
        self.current_scene = process_fields(file, SCN())
        self.json_dict["Project"]["Scene"].append(self.current_scene)
        self.current_scene["Layer"] = []

    def process_LAYR(self, file: BufferedReader, chunk_size: int) -> None:
        self.current_layer = process_fields(file, LAYR())
        self.current_scene["Layer"].append(self.current_layer)

    def process_CAST(self, file: BufferedReader, chunk_size: int) -> None:
        self.current_layer["Cast"] = []

    def process_NODE(self, file: BufferedReader, chunk_size: int) -> None:
        current_offset = file.tell()
        nodes = dict()
        nodes["Node"] = []
        validate_header(file.read(2), b'\xFC\x00')
        while file.tell() != current_offset + chunk_size:
            data = process_fields(file, NODE())
            validate_header(file.read(2), b'\x06\x05')
            validate_header(file.read(2), b'\x00\x00')
            if file.tell() == current_offset + chunk_size - 2:
                validate_header(file.read(2), b'\xFD\x00')
            else:
                validate_header(file.read(2), b'\xFE\x00')
            nodes["Node"].append(data)
        self.current_layer["Cast"].append(nodes)

    def process_TRS2(self, file: BufferedReader, chunk_size: int) -> None:
        current_offset = file.tell()
        trs2 = dict()
        trs2["Transform2D"] = []
        validate_header(file.read(2), b'\xFC\x00')
        while file.tell() != current_offset + chunk_size:
            data = process_fields(file, TRS2())
            if file.tell() == current_offset + chunk_size - 2:
                validate_header(file.read(2), b'\xFD\x00')
            else:
                validate_header(file.read(2), b'\xFE\x00')
            trs2["Transform2D"].append(data)
        self.current_layer["Cast"].append(trs2)

    def process_DATA(self, file: BufferedReader, chunk_size: int) -> None:
        self.current_data["CastData"] = []
        self.current_layer["Cast"].append(self.current_data)

    def process_CSLI(self, file: BufferedReader, chunk_size: int) -> None:
        file.read(chunk_size)

    def process_CIMG(self, file: BufferedReader, chunk_size: int) -> None:
        self.current_cimg["ImageCastData"] = []
        data = process_fields(file, CIMG())
        data["CropIndex"] = NoIndent(data["CropIndex"])
        self.current_cimg["ImageCastData"].append(data)
        self.current_data["CastData"].append(self.current_cimg)
        self.crop_ref_count = data["CropRefCount"][0]

    def process_TEXT(self, file: BufferedReader, chunk_size: int) -> None:
        file.read(chunk_size)

    def process_CREF(self, file: BufferedReader, chunk_size: int) -> None:
        cref = dict()
        cref["CropRef"] = []
        for i in range(self.crop_ref_count):
            data = process_fields(file, CREF())
            cref["CropRef"].append(data)
        self.current_cimg["ImageCastData"].append(cref)

    def process_NCAT(self, file: BufferedReader, chunk_size: int) -> None:
        file.read(chunk_size)
        self.current_layer["Animation"] = []

    def process_CATR(self, file: BufferedReader, chunk_size: int) -> None:
        file.read(chunk_size)

    def process_ANIM(self, file: BufferedReader, chunk_size: int) -> None:
        data = process_fields(file, ANIM())
        self.current_layer["Animation"].append(data)
        self.current_anim = data
        self.current_anim["Motion"] = []

    def process_MOT(self, file: BufferedReader, chunk_size: int) -> None:
        data = process_fields(file, MOT())
        self.current_anim["Motion"].append(data)
        self.current_motion = data
        self.current_motion["Track"] = []

    def process_TRK(self, file: BufferedReader, chunk_size: int) -> None:
        data = process_fields(file, TRK())
        self.current_motion["Track"].append(data)
        self.current_trk = data
        self.current_trk["Key"] = []

    def process_KEY(self, file: BufferedReader, chunk_size: int) -> None:
        key_count = self.current_trk["KeyCount"]
        for i in range(key_count):
            data = process_fields(file, KEY())
            self.current_trk["Key"].append(data)

    def process_TEXL(self, file: BufferedReader, chunk_size: int) -> None:
        self.json_dict["Project"]["TexList"] = []
        data = process_fields(file, TEXL())
        self.json_dict["Project"]["TexList"].append(data)
        self.current_texl = data
        self.current_texl["Texture"] = []

    def process_TEX(self, file: BufferedReader, chunk_size: int) -> None:
        data = process_fields(file, TEX())
        self.current_texl["Texture"].append(data)
        self.current_tex = data
        self.current_tex["Crop"] = []

    def process_CROP(self, file: BufferedReader, chunk_size: int) -> None:
        for i in range(self.current_tex["CropCount"]):
            data = process_fields(file, CROP())
            self.current_tex["Crop"].append(data)

    def process_CAM(self, file: BufferedReader, chunk_size: int) -> None:
        self.json_dict["Project"]["Camera"] = process_fields(file, CAM())

def bytes_to_hex(byte_string: bytes) -> str:
    return ' '.join(f'{byte:02x}' for byte in byte_string)

def validate_header(bytes_data: bytes, header_data: bytes) -> None:
    if bytes_data != header_data:
        raise Exception(f"Mismatched byte header: {bytes_to_hex(bytes_data)}, {bytes_to_hex(header_data)}")

def read_format(file: BufferedReader, format: str):
    if format == 'string':
        string_size = int.from_bytes(file.read(1))
        value = file.read(string_size).decode('utf-8')
    elif format in {'4B', '<HHHH', '<ff', '<fff'}:
        value = NoIndent(struct.unpack(format, file.read(struct.calcsize(format))))
    elif format == 'B':
        value = int.from_bytes(file.read(1))
    else:
        value = struct.unpack(format, file.read(struct.calcsize(format)))[0]
    return value

def process_fields(file: BufferedReader, data: Any) -> dict:
    for field_name, field_obj in data.__dataclass_fields__.items():
        if isinstance(getattr(data, field_name), Variable):
            while True:
                vari = getattr(data, field_name)
                object_type = struct.unpack("<H", file.read(2))[0]
                name, format = vari.input_map[object_type]
                value = read_format(file, format)
                vari.output_map[name] = value
                setattr(data, name, value)
                if name in {"KeyValue_Color_RGBA", "OutParam"}:
                    break
            result = data.__dict__
            del result[field_name]
            return result
        header_bytes = field_obj.metadata["header"]
        format = field_obj.metadata["format"]
        validate_header(file.read(len(header_bytes)), header_bytes)
        if isinstance(getattr(data, field_name), list):
            value = []
            length = field_obj.metadata["length"]
            for i in range(length):
                item_size = struct.calcsize(format)
                item_bytes = file.read(item_size)
                item_value = struct.unpack(format, item_bytes)
                if len(item_value) == 1:
                    value.append(item_value[0])
                else:
                    value.append(NoIndent(item_value))
                if i != length-1:
                    validate_header(file.read(len(header_bytes)), header_bytes)
        else:
            value = read_format(file, format)
        setattr(data, field_name, value)
    return data.__dict__

def unpack_surfboard(input_file) -> dict:
    """
    Unpack a compiled .sbscene file into a dictionary.

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

    The function will crash if a bad input file path is provided

    Examples
    --------
    >>> unpack_surfboard("/path/to/file/awesome.sbscene")
    """
    file_size = os.path.getsize(input_file)
    chunker = ChunkProcessor()
    process_definitions = {
        'PROJ': chunker.process_PROJ,
        'SCN ': chunker.process_SCN,
        'LAYR': chunker.process_LAYR,
        'CAST': chunker.process_CAST,
        'NODE': chunker.process_NODE,
        'TRS2': chunker.process_TRS2,
        'DATA': chunker.process_DATA,
        'CSLI': chunker.process_CSLI,
        'CIMG': chunker.process_CIMG,
        'TEXT': chunker.process_TEXT,
        'CREF': chunker.process_CREF,
        'NCAT': chunker.process_NCAT,
        'CATR': chunker.process_CATR,
        'ANIM': chunker.process_ANIM,
        'MOT ': chunker.process_MOT,
        'TRK ': chunker.process_TRK,
        'KEY ': chunker.process_KEY,
        'TEXL': chunker.process_TEXL,
        'TEX ': chunker.process_TEX,
        'CROP': chunker.process_CROP,
        'CAM ': chunker.process_CAM
    }

    with open(input_file, "rb") as f:
        _signature = f.read(32)
        while f.tell() != file_size:
            _header = f.read(4)
            chunk_size = struct.unpack("<I", f.read(4))[0] - 8
            chunk_type = f.read(4).decode()
            _chunkIndex = read_format(f, '<H')
            _chunkParameterCount = read_format(f, '<H')
            process_definitions[chunk_type](f, chunk_size)
    return chunker.get_dict()
