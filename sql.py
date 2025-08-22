from os import PathLike
from sqlite3 import Connection

from data import DHSectionData
from decompress import CompressionMode


def _to_section_data_(raw: tuple[int, int, int, bytes, bytes, bytes, int, int]):
    return DHSectionData((raw[0], raw[1]), raw[2], raw[3], raw[4], raw[5], raw[6], CompressionMode(raw[7]))

class DHDBConn:
    def __init__(self, file: str | bytes | PathLike[str] | PathLike[bytes]):
        self.conn = Connection(file)

    def get_section_poses(self) -> list[tuple[int, int]]:
        cur = self.conn.cursor()
        cur.execute("SELECT PosX, PosZ FROM FullData WHERE DetailLevel = 0")
        return cur.fetchall()

    def get_section(self, x:int, z:int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT PosX, PosZ, MinY, Data, ColumnWorldCompressionMode, Mapping, DataFormatVersion, CompressionMode FROM FullData WHERE DetailLevel = 0 and PosX = :pos_x and PosZ = :pos_z;",
            {"pos_x": x, "pos_z": z}
        )
        section = _to_section_data_(cur.fetchone())
        return section


