from itertools import product
from typing import Sequence, Callable

from anvil import EmptyRegion, Block

import data
from data import DHSectionData, DH_SECTION_WIDTH

# section_pos // 8 = region_pos
SECTION_REGION_SCALE = 512 // DH_SECTION_WIDTH

Y_OFFSET = -64

class DHData2WorldGenerator:
    def __init__(self, section_poses: Sequence[tuple[int, int]], request_section: Callable[[int, int], DHSectionData]):
        self.section_poses = set(section_poses)
        self.request_section = request_section

    def generate(self):
        while len(self.section_poses) > 0:
            section_pos = self.section_poses.pop()
            self.section_poses.add(section_pos)
            region_pos = (
                section_pos[0] // SECTION_REGION_SCALE,
                section_pos[1] // SECTION_REGION_SCALE,
            )
            print(region_pos)
            region_snapped_section_pos = (
                region_pos[0] * SECTION_REGION_SCALE,
                region_pos[1] * SECTION_REGION_SCALE,
            )

            region = EmptyRegion(region_pos[0], region_pos[1])
            for region_section_x, region_section_z in product(range(SECTION_REGION_SCALE), range(SECTION_REGION_SCALE)):
                section_pos = (region_snapped_section_pos[0]+region_section_x, region_snapped_section_pos[1]+region_section_z)
                if section_pos not in self.section_poses: continue
                self.section_poses.remove(section_pos)
                dh_section = self.request_section(*section_pos)
                palette = [(elem.biome, elem.to_block()) for elem in dh_section.mapping]
                if len(palette) > 16: palette = palette[0:16]
                for x, z in product(range(DH_SECTION_WIDTH), range(DH_SECTION_WIDTH)):
                    data_points = dh_section.data[x*DH_SECTION_WIDTH+z]
                    x, z = section_pos[0] * DH_SECTION_WIDTH + x, section_pos[1] * DH_SECTION_WIDTH + z
                    print(x, z)
                    for data_point in data_points:
                        if len(palette) <= data_point.id: continue
                        biome, block = palette[data_point.id]
                        if block is None: continue
                        min_y = data_point.min_y + Y_OFFSET
                        for y in range(min_y, min_y + data_point.height):
                            region.set_block(block, x, y, z)
            yield region_pos[0], region_pos[1], region