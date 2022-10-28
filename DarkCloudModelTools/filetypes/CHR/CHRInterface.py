from .CHRBinary import CHRBinary
from ..CFG.CFGInterface import CFGInterface
from ..MDS.MDSInterface import MDSInterface

class CHRInterface:
    def __init__(self):
        self.files = {}
    
    @classmethod
    def from_file(cls, filepath):
        binary = CHRBinary()
        binary.read(filepath)
        return cls.from_binary(binary)
        
    def to_file(self, filepath):
        binary = self.to_binary()
        binary.write(filepath)

        
    @classmethod
    def from_binary(cls, binary):
        instance = cls()
        for file in binary.files:
            name, _, _ = file.name_buffer.partition(b'\x00')
            name = name.decode('ascii')
            
            # Messy, would prefer to be able to call a "to_interface" method
            # on each Binary
            if name.endswith(".cfg"):
                instance.files[name] = CFGInterface.from_binary(file.file)
            elif name.endswith(".mds"):
                instance.files[name] = MDSInterface.from_binary(file.file)
            else:
                instance.files[name] = file.file
        return instance
        
    def to_binary(self):
        raise NotImplementedError
