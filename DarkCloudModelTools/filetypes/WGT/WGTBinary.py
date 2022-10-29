from ...serialisation.Serializable import Serializable

class WGTBinary(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.groups = []
        
    def __repr__(self):
        return f"[WGT] {self.groups}"
    
    def read_write(self, rw):
        if rw.mode() == "read":
            self.groups = []
            while rw.peek_bytestring(1) != b'':
                group = self.VertexGroup()
                rw.rw_obj(group)
                self.groups.append(group)
        else:
            self.groups = rw.rw_obj_array(self.groups, self.VertexGroup, len(self.groups))
        
    class VertexGroup(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            
            self.meshbone_idx = None
            self.bone_idx     = None
            self.unknown_0x08 = None
            self.header_size  = None
            self.elem_count   = None
            self.total_size   = None
            self.unknown_0x18 = None
            self.unknown_0x1C = None
            
            self.elements = []
            
        def __repr__(self):
            return f"[WGT::VertexGroup] {self.meshbone_idx} {self.bone_idx} {self.unknown_0x08} {self.header_size} {self.elem_count} {self.total_size} {self.unknown_0x18} {self.unknown_0x1C} {self.elements}"
        
        def read_write(self, rw):
            self.meshbone_idx = rw.rw_uint32(self.meshbone_idx)
            self.bone_idx     = rw.rw_uint32(self.bone_idx)
            self.unknown_0x08 = rw.rw_uint32(self.unknown_0x08)
            self.header_size  = rw.rw_uint32(self.header_size)
            self.elem_count   = rw.rw_uint32(self.elem_count)
            self.total_size   = rw.rw_uint32(self.total_size)
            self.unknown_0x18 = rw.rw_uint32(self.unknown_0x18)
            self.unknown_0x1C = rw.rw_uint32(self.unknown_0x1C)
            rw.assert_equal(self.unknown_0x08, 20)
            rw.assert_equal(self.header_size, 32)
            #rw.assert_equal(self.unknown_0x18, 20310152)
            #rw.assert_equal(self.unknown_0x1C, 20322672)
            
            self.elements = rw.rw_obj_array(self.elements, self.Element, self.elem_count)
            
        class Element(Serializable):
            def __init__(self, context=None):
                super().__init__(context)
                
                self.index        = None
                self.unknown_0x04 = None
                self.unknown_0x08 = None
                self.unknown_0x0C = None
                self.weight       = None
                self.unknown_0x14 = None
                self.unknown_0x18 = None
                self.unknown_0x1C = None
                
                self.elements = []
                
            def __repr__(self):
                return f"[WGT::Group::Element] {self.index} {self.unknown_0x04} {self.unknown_0x08} {self.unknown_0x0C} {self.weight} {self.unknown_0x14} {self.unknown_0x18} {self.unknown_0x1C}"
            
            def read_write(self, rw):
                self.index        = rw.rw_uint32(self.index)
                self.unknown_0x04 = rw.rw_uint32(self.unknown_0x04)
                self.unknown_0x08 = rw.rw_uint32(self.unknown_0x08)
                self.unknown_0x0C = rw.rw_uint32(self.unknown_0x0C)
                self.weight       = rw.rw_float32(self.weight)
                self.unknown_0x14 = rw.rw_uint32(self.unknown_0x14)
                self.unknown_0x18 = rw.rw_uint32(self.unknown_0x18)
                self.unknown_0x1C = rw.rw_uint32(self.unknown_0x1C)
                # rw.assert_equal(self.unknown_0x04, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(self.unknown_0x08, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(self.unknown_0x0C, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(0 <= self.weight <= 100, True) # Apparently not always the case?
                # rw.assert_equal(self.unknown_0x14, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(self.unknown_0x18, 0) # can be 0xcdcdcdcd
                # rw.assert_equal(self.unknown_0x1C, 0) # can be 0xcdcdcdcd
