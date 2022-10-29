from ...serialisation.Serializable import Serializable

class MOTBinary(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.animations = []

    def __repr__(self):
        return f"[MOT] {self.animations}"

    def read_write(self, rw):
        if rw.mode() == "read":
            while rw.peek_bytestring(1) != b'':
                anim = self.Animation()
                rw.rw_obj(anim)
                self.animations.append(anim)
        else:
            self.animations = rw.rw_obj_array(self.animations, self.Animation, len(self.animations))
            
    class Animation(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
                        
            self.unknown_0x00   = None
            self.unknown_0x04   = None
            self.data_type      = None
            self.header_size    = None
            
            self.frame_count    = None
            self.next_anim_jump = None
            self.unknown_0x18   = None
            self.unknown_0x1C   = None
            
            self.frames = []
        
        def __repr__(self):
            return f"[MOT::Animation] {self.unknown_0x00} {self.unknown_0x04} {self.data_type} {self.header_size} {self.frame_count} {self.next_anim_jump} {self.unknown_0x18} {self.unknown_0x1C} "
    
        def read_write(self, rw):
            self.unknown_0x00   = rw.rw_uint32(self.unknown_0x00) # Bone IDX?
            self.unknown_0x04   = rw.rw_uint32(self.unknown_0x04) # Anim IDX?
            self.data_type      = rw.rw_uint32(self.data_type)
            self.header_size    = rw.rw_uint32(self.header_size)
            
            self.frame_count    = rw.rw_uint32(self.frame_count)
            self.next_anim_jump = rw.rw_uint32(self.next_anim_jump)
            self.unknown_0x18   = rw.rw_uint32(self.unknown_0x18)
            self.unknown_0x1C   = rw.rw_uint32(self.unknown_0x1C)
            
            rw.assert_equal(self.header_size, 32)
            
            self.frames = rw.rw_obj_array(self.frames, self.Frame, self.frame_count)
            
        class Frame(Serializable):
            def __init__(self, context=None):
                super().__init__(context)
                
                self.unknown_0x00 = None
                self.unknown_0x04 = None
                self.unknown_0x08 = None
                self.unknown_0x0C = None
                
                self.unknown_0x10 = None
                self.unknown_0x14 = None
                self.unknown_0x18 = None
                self.unknown_0x1C = None
                
            def __repr__(self):
                return f"[MOT::Animation::Frame] {self.unknown_0x00} {self.unknown_0x10} {self.unknown_0x14} {self.unknown_0x18} {self.unknown_0x1C}"
            
            def read_write(self, rw):
                self.unknown_0x00 = rw.rw_uint32(self.unknown_0x00)
                self.unknown_0x04 = rw.rw_uint32(self.unknown_0x04)
                self.unknown_0x08 = rw.rw_uint32(self.unknown_0x08)
                self.unknown_0x0C = rw.rw_uint32(self.unknown_0x0C)
                
                self.unknown_0x10 = rw.rw_float32(self.unknown_0x10)
                self.unknown_0x14 = rw.rw_float32(self.unknown_0x14)
                self.unknown_0x18 = rw.rw_float32(self.unknown_0x18)
                self.unknown_0x1C = rw.rw_float32(self.unknown_0x1C)
                
                # rw.assert_equal(self.unknown_0x04, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(self.unknown_0x08, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(self.unknown_0x0C, 0) # can be 0xcdcdcdcd
