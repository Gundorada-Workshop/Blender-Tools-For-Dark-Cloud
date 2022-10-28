from .Serializable import Serializable


class PointerIndexableArray(Serializable):
    def __init__(self, context):
        super().__init__(context)
        #self.context.anchor_pos = context.anchor_pos
        #self.context.endianness = context.endianness
        
        self.data = []
        self.ptr_to_idx = {}
        self.idx_to_ptr = {}
        
    def at_ptr(self, ptr):
        return self.data[self.ptr_to_idx[ptr]]
    
    def at_idx(self, idx):
        return self.data[idx]

    def __getitem__(self, idx):
        return self.data[idx]

    def __iter__(self):
        for elem in self.data:
            yield elem
    
    def read_write(self, rw, *args, **kwargs):
        for i, elem in enumerate(self.data):
            if i in self.idx_to_ptr:
                rw.assert_local_file_pointer_now_at("Start of Array Entry", self.idx_to_ptr[i])
            curpos = rw.local_tell()
            self.ptr_to_idx[curpos] = i
            self.idx_to_ptr[i] = curpos

            self.rw_element(rw, i, *args, **kwargs)
            

    def rw_element(self, rw, idx, *args, **kwargs):
        rw.rw_obj(self.data[idx], *args, **kwargs)
        
    def rw_element_method(self, rw, func, idx):
        rw.rw_obj_method(self.data[idx], getattr(self.data[idx], func.__name__))
        
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return f"[Pointer Indexable Array]: {self.data}"
    
class PointerIndexableArrayInt8(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_int8(self.data[idx])
    
class PointerIndexableArrayUint8(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_uint8(self.data[idx])
    
class PointerIndexableArrayInt16(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_int16(self.data[idx])
    
class PointerIndexableArrayUint16(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_uint16(self.data[idx])
    
class PointerIndexableArrayInt32(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_int32(self.data[idx])
    
class PointerIndexableArrayUint32(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_uint32(self.data[idx])
    
class PointerIndexableArrayInt64(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_int64(self.data[idx])
    
class PointerIndexableArrayUint64(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_uint64(self.data[idx])
    
class PointerIndexableArrayFloat16(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_float16(self.data[idx])
    
class PointerIndexableArrayFloat32(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_float32(self.data[idx])
    
class PointerIndexableArrayFloat64(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_float64(self.data[idx])
    
class PointerIndexableArrayPointer(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_pointer(self.data[idx])
    
class PointerIndexableArrayMatrix4x4(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_matrix4x4(self.data[idx])
    
class PointerIndexableArrayVec32(PointerIndexableArray):
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_vec32(self.data[idx])
    
class PointerIndexableArrayCStr(PointerIndexableArray):
    def __init__(self, context, encoding='ascii'):
        super().__init__(context)
        self.encoding = encoding
        
    def rw_element(self, rw, idx): self.data[idx] = rw.rw_cstr(self.data[idx], encoding=self.encoding)
