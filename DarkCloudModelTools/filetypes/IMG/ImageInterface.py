import struct

class ImageInterface:
    def __init__(self):
        self.pixels = []
        
    @classmethod
    def from_TM2(cls, tm2):
        instance = cls()
        
        # Parse CLUT first, since it may be needed later
        clut = cls.__parse_clut(tm2)
        
        # Now parse the image data        
        image_colour_type = tm2.header.image_colour_type
        if image_colour_type == 5:
            clut_indices = struct.unpack('B'*len(tm2.texture), tm2.texture)
            instance.pixels = [clut[idx] for idx in clut_indices]
        else:
            raise NotImplementedError(f"Unhandled TIM2 Image Colour Type: {image_colour_type}")
            
        return instance
            
    def to_TM2(self):
        raise NotImplementedError
        
    @staticmethod
    def __parse_clut(tm2):
        # Set up convenience variables
        is_linear = (tm2.header.clut_colour_type & 0x80) != 0
        clut_colour_type = tm2.header.clut_colour_type & 0x7F
        clut_colour_count = tm2.header.clut_colour_count
        image_colour_type = tm2.header.image_colour_type
        
        # Determine clut colour size
        if image_colour_type == 5:
            clut_colour_size = (clut_colour_type & 0x07) + 1
        else:
            raise NotImplementedError(f"Unhandled TIM2 Image Colour Type: {image_colour_type}")
            
        # Parse each palette
        palette_count = tm2.header.clut_size // (clut_colour_size * clut_colour_count)
        palette_size = tm2.header.clut_size // palette_count
        palettes = []
        # Not sure how to handle multiple palettes yet...
        assert palette_count == 1
        for i in range(palette_count):
            if clut_colour_size == 2: # 16BITLE_ABGR_5551 Format
                palette_colour_count = palette_size//2
                palette = struct.unpack('H'*palette_colour_count, tm2.clut)
                for palette_idx, palette_value in enumerate(palette):
                    colour = [None, None, None, None]
                    colour[0] = ((palette_value >> 11) & 0x05) / 31
                    colour[1] = ((palette_value >>  6) & 0x05) / 31
                    colour[2] = ((palette_value >>  1) & 0x05) / 31
                    colour[3] = ((palette_value >>  0) & 0x01) /  1
                    palette[palette_idx] = colour
            elif clut_colour_size == 3: # 24BIT_RGB Format
                palette_colour_count = palette_size//3
                palette = struct.unpack('B'*palette_colour_count*3, tm2.clut)
                palette = [
                    [a/255, b/255, c/255, 1.] 
                    for a, b, c in zip(palette[0::3], 
                                       palette[1::3], 
                                       palette[2::3])
                ]
            elif clut_colour_size == 4: # 32BIT_RGBA Format
                palette_colour_count = palette_size//4
                palette = struct.unpack('B'*palette_colour_count*4, tm2.clut)
                palette = [
                    [a/255, b/255, c/255, d/255] 
                    for a, b, c, d in zip(palette[0::4], 
                                          palette[1::4], 
                                          palette[2::4],
                                          palette[3::4])
                ]
            else:
                raise ValueError(f"Invalid CLUT colour count: {clut_colour_count}")
                 
            if (not is_linear):
                parts   = palette_size // (32*4)
                stripes = 2
                colours = 8
                blocks  = 2
    
                new_idx = 0
                new_palette = [None]*len(palette)
                for part in range(parts):
                    for block in range(blocks):
                        for stripe in range(stripes):
                            for colour in range(colours):
                                old_idx  = part * colours * stripes * blocks
                                old_idx += block * colours
                                old_idx += stripe * stripes * colours
                                old_idx += colour
                                print(len(new_palette), old_idx, new_idx, parts*blocks*stripes*colours)
                                new_palette[new_idx] = palette[old_idx]
                                new_idx += 1
                palette = new_palette
            palettes.append(palette)
        return palettes[0]
                    