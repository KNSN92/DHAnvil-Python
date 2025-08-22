from itertools import product

import sql
import data
import worldgen


def main():
    conn = sql.DHDBConn("DistantHorizons.sqlite")
    conn.get_section(0, 0)
    # def request_section(x: int, z: int):
    #     return conn.get_section(x, z)
    # generator = worldgen.DHData2WorldGenerator(list(product(range(-4, 4), range(-4, 4))), request_section)
    # for x, z, region in generator.generate():
    #     region.save(f"r.{x}.{z}.mca")
        # for y in range(-64, 320):
        #     print(y, region.get_chunk(0, 0).get_block(0, y, 0))

if __name__ == "__main__":
    main()