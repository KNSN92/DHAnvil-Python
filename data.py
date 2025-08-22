from io import BytesIO
from typing import Optional

from anvil import Block

from decompress import CompressionMode

DH_SECTION_WIDTH = 64

class DHFullDataPoint:
    def __init__(self, id: int, height: int, min_y: int):
        self.id = id
        self.height = height
        self.min_y = min_y

def read_bytes_to_full_data_points(buf: BytesIO):
    data_list: list[list[DHFullDataPoint]] = [[] for _ in range(DH_SECTION_WIDTH*DH_SECTION_WIDTH)]
    for xz in range(DH_SECTION_WIDTH*DH_SECTION_WIDTH):
        data_col_len = int.from_bytes(buf.read(2))
        if data_col_len < 0:
            print(f"Read DataSource Blob data at index [{xz}], column length [{xz}] should be greater than zero.")
        data_col: list[DHFullDataPoint | None] = [None for _ in range(data_col_len)]
        for y in range(data_col_len):
            data = int.from_bytes(buf.read(8))
            data_id = data & 2147483647
            data_height = (data >> 32) & 4095
            data_min_y = (data >> 44) & 4095
            data_col[y] = DHFullDataPoint(data_id, data_height, data_min_y)
        data_list[xz] = data_col
    return data_list

class DHMappingElement:
    def __init__(self, biome: str, block: str | None, block_state: Optional[dict[str, str]] = None):
        self.biome = biome
        self.block = block
        self.block_state = block_state

    def get_biome(self):
        return self.biome

    def to_block(self):
        if self.block is None: return None
        namespace, block_id = self.block.split(":")
        return Block(namespace, block_id, self.block_state)

    def __repr__(self):
        block = self.block if self.block is not None else "AIR"
        block_state = "[" + ", ".join([f"{k}={v}" for k, v in self.block_state.items()]) + "]" if self.block_state is not None else ""
        return f"{self.biome} {block}{block_state}"

def read_bytes_to_mappings(buf: BytesIO):
    state_len = int.from_bytes(buf.read(4))
    if state_len <= 0:
        print("There are no contents.")
    mappings: list[DHMappingElement] = []
    for _ in range(state_len):
        utf_len = int.from_bytes(buf.read(2))
        read = buf.read(utf_len).decode()
        if "_DH-BSW_" not in read:
            print(f"Failed to deserialize BiomeBlockStateEntry [{read}], unable to find separator.")
            exit(1)
        biome, block_state = read.split("_DH-BSW_")

        if "_STATE_" in block_state:
            block, states = block_state.split("_STATE_")
            if block == "AIR":
                mappings.append(DHMappingElement(biome, None))
            else:
                if len(states) > 0:
                    state_dict = {}
                    for state in states[1:-1].split("}{"):
                        key, value = state.split(":")
                        state_dict[key] = value
                    mappings.append(DHMappingElement(biome, block, state_dict))
                else:
                    mappings.append(DHMappingElement(biome, block))
        else:
            block = block_state
            if block == "AIR":
                mappings.append(DHMappingElement(biome, None))
            else:
                mappings.append(DHMappingElement(biome, block))
    return mappings

class DHSectionData:
    def __init__(self, pos: tuple[int, int], min_y: int, data: bytes, column_world_compression_mode: bytes, mapping: bytes, data_format_version: int, compression_mode: CompressionMode):
        self.pos = pos
        self.min_y = min_y
        self.data = read_bytes_to_full_data_points(BytesIO(compression_mode.decompress(data)))
        self.column_world_compression_mode = column_world_compression_mode
        self.mapping = read_bytes_to_mappings(BytesIO(compression_mode.decompress(mapping)))
        self.data_format_version = data_format_version
        self.compression_mode = compression_mode
