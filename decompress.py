from enum import Enum
from lzma import LZMADecompressor, FORMAT_AUTO


class CompressionMode(Enum):
    Uncompressed = 0
    Lz4 = 1
    Lzma2 = 3

    def decompress(self, data: bytes):
        match self:
            case CompressionMode.Uncompressed:
                return data
            case CompressionMode.Lz4:
                print("LZ4 Compression is not supported")
                exit(1)
            case CompressionMode.Lzma2:
                return decompress_lzma(data)
        return None

def decompress_lzma(data):
    results = []
    while True:
        decomp = LZMADecompressor(FORMAT_AUTO, None, None)
        try:
            res = decomp.decompress(data)
        except LZMAError:
            if results:
                break  # Leftover data is not a valid LZMA/XZ stream; ignore it.
            else:
                raise  # Error on the first iteration; bail out.
        results.append(res)
        data = decomp.unused_data
        if not data:
            break
        if not decomp.eof:
            raise LZMAError("Compressed data ended before the end-of-stream marker was reached")
    return b"".join(results)