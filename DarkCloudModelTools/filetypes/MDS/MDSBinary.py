from ...serialisation.Serializable import Serializable
from ...serialisation.PointerIndexableArray import PointerIndexableArray

class MDSBinary(Serializable):

    class Contents(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            self.filetype = b"MDS\x00"
            self.unknown_0x04 = None
            self.bone_count = None
            self.mdt_count = None
            
        def __repr__(self):
            return f"[MDS::Contents] {self.filetype} {self.unknown_0x04} {self.bone_count} {self.mdt_count}"
            
        def read_write(self, rw):
            self.filetype = rw.rw_bytestring(self.filetype, 4)
            assert self.filetype == b"MDS\x00"
            self.unknown_0x04 = rw.rw_uint32(self.unknown_0x04)
            assert self.unknown_0x04 == 1
            self.bone_count = rw.rw_uint32(self.bone_count)
            self.mdt_count  = rw.rw_uint32(self.mdt_count)
            
    def __init__(self, context=None):
        super().__init__(context)
        self.contents = self.Contents()
        self.bones = []
        self.mdts  = PointerIndexableArray(self.context)
    
    def read_write(self, rw):
        rw.rw_obj(self.contents)
        self.rw_bones(rw)
        self.rw_mdts(rw)
        if rw.mode() == "read":
            assert rw.peek_bytestring(1) == b''
        
    def rw_bones(self, rw):
        self.bones = rw.rw_obj_array(self.bones, Bone, self.contents.bone_count)
        
    def rw_mdts(self, rw):
        count = len(set(b.mdt_offset for b in self.bones)) # Does not equal 'MDT count'...
        if rw.mode() == "read":
            self.mdts.data = [MDT() for _ in range(count)]
        rw.rw_obj(self.mdts)
    

class Bone(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        self.index       = None
        self.header_size = 0x70
        self.name        = None
        self.mdt_offset  = None
        self.parent      = None
        self.matrix      = None
        
    def __repr__(self):
        pad = b'\x00'
        return f"[MDS::Bone] {self.index} {self.header_size} {self.name.rstrip(pad).decode('ascii')} {self.mdt_offset} {self.parent} {list(self.matrix)}"
        
    def read_write(self, rw):
        self.index        = rw.rw_uint32(self.index)
        self.header_size  = rw.rw_uint32(self.header_size)
        self.name         = rw.rw_bytestring(self.name, 0x20)
        self.mdt_offset   = rw.rw_uint32(self.mdt_offset)
        self.parent       = rw.rw_int32(self.parent)
        self.matrix       = rw.rw_float32s(self.matrix, 16)
        
class MDT(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        self.contents   = self.Contents()
        self.positions  = []
        self.unknown_1s = []
        self.faces      = MeshIndices()
        self.normals    = []
        self.UVs        = []
        self.unknown_3s = []
        
    def __repr__(self):
        return f"[MDS::MDT] {self.contents}"
        
    def read_write(self, rw):
        rw.anchor_pos = rw.tell()
        rw.rw_obj(self.contents)
        if self.contents.filetype == b'':
            return
        if self.contents.positions_offset > 0:
            rw.assert_local_file_pointer_now_at("Positions", self.contents.positions_offset)
            self.positions = rw.rw_float32s(self.positions, (self.contents.position_count, 4))

        if self.contents.unknown_1_offset > 0:
            rw.assert_local_file_pointer_now_at("Unknown 1", self.contents.unknown_1_offset)
            self.unknown_1s = rw.rw_float32s(self.unknown_1s, (self.contents.unknown_1_count, 4))

        if self.contents.faces_offset > 0:
            rw.assert_local_file_pointer_now_at("Faces", self.contents.faces_offset)
            rw.rw_obj(self.faces)
            
            rw.assert_local_file_pointer_now_at("End of Indices", self.contents.faces_offset + self.contents.face_count)
            remainder_count = (0x10 - (self.contents.face_count % 0x10)) % 0x10
            remainder = rw.rw_bytestring(b'\x00'*remainder_count, remainder_count)
            
        if self.contents.normals_offset > 0:
            rw.assert_local_file_pointer_now_at("Normals", self.contents.normals_offset)
            self.normals = rw.rw_float32s(self.normals, (self.contents.normal_count, 4))
            if rw.local_tell() != self.contents.UV_offset:
                res = rw.rw_bytestring(b'\x00'*0x10, 0x10)
            
        if self.contents.UV_offset > 0:
            rw.assert_local_file_pointer_now_at("UVs", self.contents.UV_offset)
            self.UVs = rw.rw_float32s(self.UVs, (self.contents.UV_count, 4))
            
        if self.contents.unknown_3_offset > 0: # Materials?
            rw.assert_local_file_pointer_now_at("Unknown 3", self.contents.unknown_3_offset)
            self.unknown_3s = rw.rw_float32s(self.unknown_3s, (self.contents.unknown_3_count, 4*6))
        
        if rw.local_tell() != self.contents.size:
            remainder = self.contents.size - rw.local_tell()
            res = rw.rw_bytestring(b'\x00'*remainder, remainder)
            
        rw.assert_local_file_pointer_now_at("End of MDT", self.contents.size)
        
        rw.anchor_pos = 0
    
    class Contents(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            self.filetype         = None
            self.unknown_0x04     = None
            self.size             = None
            
            self.position_count   = None
            self.positions_offset = None
            self.normal_count     = None
            self.normals_offset   = None
            self.unknown_1_count  = None
            self.unknown_1_offset = None
            self.face_count       = None
            self.faces_offset     = None
            self.UV_count         = None
            self.UV_offset        = None
            self.unknown_3_count  = None
            self.unknown_3_offset = None
            self.unknown_0x3C     = None
            
        def __repr__(self):
            return f"[MDS::MDT::Contents] {self.filetype} {self.unknown_0x04} {self.size} "\
                f"{self.position_count}/{self.positions_offset} "\
                f"{self.normal_count}/{self.normals_offset} "\
                f"{self.unknown_1_count}/{self.unknown_1_offset} "\
                f"{self.face_count}/{self.faces_offset} "\
                f"{self.UV_count}/{self.UV_offset} "\
                f"{self.unknown_3_count}/{self.unknown_3_offset} "\
                f"{self.unknown_0x3C}"
            
        def read_write(self, rw):
            if self.filetype == b'':
                return
            self.filetype         = rw.rw_bytestring(self.filetype, 4)
            if self.filetype == b'':
                return
            assert self.filetype == b"MDT\x00", self.filetype
            self.unknown_0x04     = rw.rw_uint32(self.unknown_0x04)
            self.size             = rw.rw_uint32(self.size)
            
            self.position_count   = rw.rw_uint32(self.position_count)
            self.positions_offset = rw.rw_int32(self.positions_offset)
            self.normal_count     = rw.rw_uint32(self.normal_count)
            self.normals_offset   = rw.rw_int32(self.normals_offset)
            self.unknown_1_count  = rw.rw_uint32(self.unknown_1_count)
            self.unknown_1_offset = rw.rw_int32(self.unknown_1_offset)
            self.face_count       = rw.rw_uint32(self.face_count)
            self.faces_offset     = rw.rw_int32(self.faces_offset)
            self.UV_count         = rw.rw_uint32(self.UV_count)
            self.UV_offset        = rw.rw_int32(self.UV_offset)
            self.unknown_3_count  = rw.rw_uint32(self.unknown_3_count)
            self.unknown_3_offset = rw.rw_int32(self.unknown_3_offset)
            self.unknown_0x3C     = rw.rw_bytestring(self.unknown_0x3C, 4)
            
class MeshIndices(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.unknown_0x00 = None
        self.unknown_0x04 = None
        self.strip_count = None
        self.unknown_0x0C = None
        
        self.strips = []
        
    def __repr__(self):
        return f"[MDS::MDT::FaceGroup] {self.unknown_0x00} {self.unknown_0x04} {self.strip_count} {self.unknown_0x0C}"
        
    def read_write(self, rw):
        self.unknown_0x00 = rw.rw_uint32(self.unknown_0x00)
        self.unknown_0x04 = rw.rw_uint32(self.unknown_0x04)
        self.strip_count  = rw.rw_uint32(self.strip_count)
        self.unknown_0x0C = rw.rw_uint32(self.unknown_0x0C)
        
        self.strips = rw.rw_obj_array(self.strips, Strip, self.strip_count)

class Strip(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.type = None
        self.is_wide_vertex = None
        self.vertex_count = None
        self.texture_idx = None
        
        self.indices = []
        
    def __repr__(self):
        return f"[MDS::MDT::Strip] {self.type} {self.is_wide_vertex} {self.vertex_count} {self.texture_idx} {self.indices}"
        
    def read_write(self, rw):
        self.type           = rw.rw_uint16(self.type)
        self.is_wide_vertex = rw.rw_uint16(self.is_wide_vertex)
        self.vertex_count   = rw.rw_uint32(self.vertex_count)
        self.texture_idx    = rw.rw_uint32(self.texture_idx)
        
        self.indices = rw.rw_uint32s(self.indices, (self.vertex_count, 4 if self.is_wide_vertex else 3))
        