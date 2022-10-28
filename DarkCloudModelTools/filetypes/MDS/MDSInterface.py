import importlib
import sys

from .MDSBinary import MDSBinary
from .MDSBinary import MDT
    
class MDSInterface:
    def __init__(self):
        self.bones = []
        self.meshes = []
        
    @classmethod
    def from_file(cls, filepath):
        mds = MDSBinary()
        mds.read(filepath)
        return cls.from_binary(mds)
    
    def to_file(self, filepath):
        raise NotImplementedError
        
    @classmethod
    def from_binary(cls, mds):
        instance = cls()
        instance.bones  = [BoneInterface.from_binary(bone, mds.mdts) for bone in mds.bones]
        instance.meshes = [MDTInterface.from_binary(mdt) for mdt in mds.mdts]
        return instance
        
    def to_binary(self):
        raise NotImplementedError

class BoneInterface:
    def __init__(self):
        self.name    = None
        self.parent  = None
        self.matrix  = None
        self.mdt_idx = None
        
    def __repr__(self):
        return f"[BoneInterface] {self.name} {self.parent} {self.matrix} {self.mdt_idx}"

    @classmethod
    def from_binary(cls, bone, mdts):
        instance = cls()
        instance.name = bone.name.partition(b'\x00')[0].decode('ascii')
        instance.parent = bone.parent
        instance.matrix = bone.matrix
        instance.mdt_idx = mdts.ptr_to_idx.get(bone.mdt_offset)
        return instance
    
    def to_binary(self):
        raise NotImplementedError
        
class MDTInterface:
    def __init__(self):
        self.vertices  = []
        self.faces     = []
        self.materials = []
    
    @classmethod
    def from_binary(cls, mdt):
        instance = cls()
        
        instance.vertices = [v[:3] for v in mdt.positions]
        normals = [list(p[:3]) for p in mdt.normals]
        uvs     = [list(p[:2]) for p in mdt.UVs]
        instance.materials = [Material.from_binary(m) for m in mdt.materials]
        
        # Generate faces
        instance.faces = []
        for element in mdt.faces.strips:
            if element.type == 3: # Triangles
                for a, b, c in zip(element.indices[::3], element.indices[1::3], element.indices[2::3]):
                    instance.faces.append(cls.__make_face(a, b, c, normals, uvs, element))
            elif element.type == 4: # Triangle strips
                for idx, (a, b, c) in enumerate(zip(element.indices, element.indices[1:], element.indices[2:])):
                    if idx % 2 == 0:
                        instance.faces.append(cls.__make_face(a, b, c, normals, uvs, element))
                    else:
                        instance.faces.append(cls.__make_face(b, a, c, normals, uvs, element))
            else:
                raise NotImplementedError
        return instance
    
    def to_binary(self):
        raise NotImplementedError
        
    @staticmethod
    def __make_face(a, b, c, normals, uvs, element):
        loop_1 = Loop(a[0], normals[a[1]], uvs[a[2]])
        loop_2 = Loop(b[0], normals[b[1]], uvs[b[2]])
        loop_3 = Loop(c[0], normals[c[1]], uvs[c[2]])
        return Face(loop_1, loop_2, loop_3, element.material_idx)

class Face:
    __slots__ = ("loop_1", "loop_2", "loop_3", "material_idx")
    
    def __init__(self, loop_1, loop_2, loop_3, material_idx):
        self.loop_1 = loop_1
        self.loop_2 = loop_2
        self.loop_3 = loop_3
        self.material_idx = material_idx

class Loop:
    __slots__ = ("vertex_idx", "normal", "uv")
    
    def __init__(self, vertex_idx, normal, uv):
        self.vertex_idx = vertex_idx
        self.normal     = normal
        self.uv         = uv
        
class Material:
    __slots__ = ("unknown_0x00", "unknown_0x04", "unknown_0x08", "unknown_0x0C",
                 "unknown_0x10", "unknown_0x14", "unknown_0x18", "unknown_0x30",
                 "texture_name")
    
    def __init__(self):
        self.unknown_0x00 = None
        self.unknown_0x04 = None
        self.unknown_0x08 = None
        self.unknown_0x0C = None
        
        self.unknown_0x10 = None
        self.unknown_0x14 = None
        self.unknown_0x18 = None
        
        self.unknown_0x30 = None
        
        self.texture_name = None
        
    @classmethod
    def from_binary(cls, mat):
        instance = cls()
        instance.unknown_0x00 = mat.unknown_0x00
        instance.unknown_0x04 = mat.unknown_0x04
        instance.unknown_0x08 = mat.unknown_0x08
        instance.unknown_0x0C = mat.unknown_0x0C
        instance.unknown_0x10 = mat.unknown_0x10
        instance.unknown_0x14 = mat.unknown_0x14
        instance.unknown_0x18 = mat.unknown_0x18
        instance.unknown_0x30 = mat.unknown_0x30
        
        instance.texture_name = mat.texture_name.partition(b'\x00')[0].decode('ascii')
        
        return instance
