from ...serialisation.Serializable import Serializable

class IMGBinary(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.contents = self.Contents()
        self.image_records = []
        self.image_data = []
        
    def __repr__(self):
        return f"[IMG] {self.contents}"
    
    def read_write(self, rw):
        rw.rw_obj(self.contents)
        self.image_records = rw.rw_obj_array(self.image_records, self.ImageRecord, self.contents.count)
        self.image_data = rw.rw_obj_array(self.image_data, TIM2, self.contents.count)
    
    class Contents(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            
            self.filetype     = b'IMG\x00'
            self.count        = None
            self.unknown_0x08 = 0
            self.unknown_0x0C = 0
            
        def __repr__(self):
            return f"[IMG::Contents] {self.filetype} {self.count}"
        
        def read_write(self, rw):
            self.filetype     = rw.rw_bytestring(self.filetype, 0x04)
            self.count        = rw.rw_uint32(self.count)
            self.unknown_0x08 = rw.rw_uint32(self.unknown_0x08)
            self.unknown_0x0C = rw.rw_uint32(self.unknown_0x0C)
            
            rw.assert_equal(self.filetype, b'IMG\x00')

    class ImageRecord(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            
            self.filename     = None
            self.offset       = None
            self.unknown_0x24 = None
            self.unknown_0x28 = None
            self.unknown_0x2C = None
            
        def __repr__(self):
            return f"[IMG::ImageRecord] {self.filename} {self.offset} {self.unknown_0x24} {self.unknown_0x28} {self.unknown_0x2C}"
        
        def read_write(self, rw):
            self.filename     = rw.rw_bytestring(self.filename, 0x20)
            self.offset       = rw.rw_uint32(self.offset)
            self.unknown_0x24 = rw.rw_uint32(self.unknown_0x24)
            self.unknown_0x28 = rw.rw_uint32(self.unknown_0x28)
            self.unknown_0x2C = rw.rw_uint32(self.unknown_0x2C)
        
class TIM2(Serializable):
    """
    Binary representation of a TIM2 file.
    Thanks to [1], [2], and [3] for providing the main sources of reference for
    this class.
    [1] https://openkh.dev/common/tm2.html#tfx-register-texture-function
    [2] https://wiki.xentax.com/index.php/TM2_TIM2_Image
    [3] https://github.com/marco-calautti/Rainbow
    """
    
    def __init__(self, context=None):
        super().__init__(context)
        self.header = self.Header()
        self.images = []

    def __repr__(self):
        return f"[TIM2] {self.header}"
    
    def read_write(self, rw):
        rw.rw_obj(self.header)
        self.images = rw.rw_obj_array(self.images, self.TIM2Image, self.header.tex_count)
        
    class Header(Serializable):     
        def __init__(self, context=None):
            super().__init__(context)
            self.filetype  = b'TIM2'
            self.version   = None
            self.alignment = None
            self.tex_count = None
        
        def __repr__(self):
            return f"[TIM2::Header] {self.filetype} {self.version} {self.alignment} {self.tex_count}"
    
        def read_write(self, rw):
            self.filetype  = rw.rw_bytestring(self.filetype, 0x04)
            assert self.filetype == b'TIM2', self.filetype
            self.version   = rw.rw_uint8(self.version)
            self.alignment = rw.rw_uint8(self.alignment) # 0 or 1
            self.tex_count = rw.rw_uint16(self.tex_count)
            rw.align(rw.tell(), 0x10)
            if self.alignment == 1:
                rw.align(rw.tell(), rw.tell() + 0x70)
        
    class TIM2Image(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            self.header = self.Header()
            self.mipmaps = self.TIM2MipMap()
            self.texture = b''
            self.clut    = b''
        
        def __repr__(self):
            return f"[TIM2::Image] {self.header}"
    
        def read_write(self, rw):
            self.header  = rw.rw_obj(self.header)
            if self.header.mipmap_count > 1:
                self.mipmaps = rw.rw_obj(self.mipmaps)
            self.texture = rw.rw_bytestring(self.texture, self.header.image_size)
            self.clut    = rw.rw_bytestring(self.clut, self.header.clut_size)
            
        class Header(Serializable):     
            def __init__(self, context=None):
                super().__init__(context)
                self.total_size        = None
                self.clut_size         = None
                self.image_size        = None
                self.header_size       = None
                self.clut_colour_count = None
                self.image_format      = None
                self.mipmap_count      = None
                self.clut_colour_type  = None
                self.image_colour_type = None
                self.image_width       = None
                self.image_height      = None
                self.gs_tex_reg_1      = None
                self.gs_tex_reg_2      = None
                self.gs_flags_reg      = None
                self.gs_clut_reg       = None
                self.user_data         = None
            
            def __repr__(self):
                return f"[TIM2::Image::Header] {self.total_size} {self.clut_size} "\
                       f"{self.image_size} {self.header_size} {self.clut_colour_count} "\
                       f"{self.image_format} {self.mipmap_count} {self.clut_colour_type} "\
                       f"{self.image_colour_type} {self.image_width} {self.image_height} "\
                       f"{self.gs_tex_reg_1} {self.gs_tex_reg_2} "\
                       f"{self.gs_flags_reg} {self.gs_clut_reg}"    
        
            def read_write(self, rw):
                self.total_size        = rw.rw_uint32(self.total_size)
                self.clut_size         = rw.rw_uint32(self.clut_size)
                self.image_size        = rw.rw_uint32(self.image_size)
                self.header_size       = rw.rw_uint16(self.header_size)
                self.clut_colour_count = rw.rw_uint16(self.clut_colour_count)
                self.image_format      = rw.rw_uint8(self.image_format)
                self.mipmap_count      = rw.rw_uint8(self.mipmap_count)
                self.clut_colour_type  = rw.rw_uint8(self.clut_colour_type)
                self.image_colour_type = rw.rw_uint8(self.image_colour_type)
                self.image_width       = rw.rw_uint16(self.image_width)
                self.image_height      = rw.rw_uint16(self.image_height)
                self.gs_tex_reg_1      = rw.rw_uint64(self.gs_tex_reg_1)
                self.gs_tex_reg_2      = rw.rw_uint64(self.gs_tex_reg_2)
                self.gs_flags_reg      = rw.rw_uint32(self.gs_flags_reg)
                self.gs_clut_reg       = rw.rw_uint32(self.gs_clut_reg)
                self.user_data         = rw.rw_bytestring(self.user_data, self.header_size - 0x30)
                
                rw.assert_equal(self.gs_tex_reg_1, 0)
                rw.assert_equal(self.gs_flags_reg, 0)
                rw.assert_equal(self.gs_clut_reg, 0)
                
        class TIM2MipMap(Serializable):
            def __init__(self, context=None):
                super().__init__(context)
                self.reg_1 = None
                self.reg_2 = None
                self.reg_3 = None
                self.reg_4 = None
                self.sizes = []
            
            def __repr__(self):
                return f"[TIM2::MipMap] {self.reg_1} {self.reg_2} {self.reg_3} {self.reg_4} {self.sizes}"
        
            def read_write(self, rw):
                self.reg_1  = rw.rw_uint32(self.reg_1)
                self.reg_2  = rw.rw_uint32(self.reg_2)
                self.reg_3  = rw.rw_uint32(self.reg_3)
                self.reg_4  = rw.rw_uint32(self.reg_4)
                self.sizes  = rw.rw_uint32s(self.sizes, 8)
                