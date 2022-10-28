from ...serialisation.Serializable import Serializable

class BBPBinary(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.bpms = []
        
    def __repr__(self):
        return f"[BBP] {self.bpms}"
    
    def read_write(self, rw):
        if rw.mode() == "read":
            self.bpms = []
            while rw.peek_bytestring(1) != b'':
                self.bpms.append(rw.rw_float32s(None, 16))
        else:
            self.bpms = rw.rw_float32s(self.bpms, (len(self.bpms), 4*4))
            
        if rw.mode() == "read":
            assert rw.peek_bytestring(1) == b'', rw.peek_bytestring(0x40)
