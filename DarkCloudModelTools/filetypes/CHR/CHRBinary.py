import io

from ..MOT.MOTBinary import MOTBinary
from ..TXT.TXTBinary import TextBinary
from ..MDS.MDSBinary import MDSBinary
from ..BBP.BBPBinary import BBPBinary
from ..WGT.WGTBinary import WGTBinary
from ..IMG.IMGBinary import IMGBinary
from ..IMG.IMGBinary import IM2Binary
from ...serialisation.BinaryTargets import Reader, Writer
from ...serialisation.Serializable import Serializable

class CHRBinary(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.files = []
        
    def __repr__(self):
        return f"[CHR] {self.files}"
    
    def read_write(self, rw):
        if rw.mode() == "read":
            while rw.peek_bytestring(1) != b'':
                file = self.File()
                rw.rw_obj(file)
                self.files.append(file)
        else:
            self.files = rw.rw_obj_array(self.files, self.File, len(self.files))
        
    class File(Serializable):
        def __init__(self, context=None):
            super().__init__(context)
            
            self.name_buffer    = None
            self.header_size    = 0x50
            self.file_size      = None
            self.next_file_jump = None
            self.unknown_0x0C   = None
            self.file           = None
            
        def __repr__(self):
            pad = b'\x00'
            filename = self.name_buffer.split(pad)[0].decode('ascii') if self.name_buffer is not None else None
            return f"[CHR::File] {self.header_size} {self.file_size} {self.next_file_jump} {self.unknown_0x0C} {filename}"
    
        def read_write(self, rw):
            self.name_buffer    = rw.rw_bytestring(self.name_buffer, 0x40)
            self.header_size    = rw.rw_uint32(self.header_size)
            self.file_size      = rw.rw_uint32(self.file_size)
            self.next_file_jump = rw.rw_uint32(self.next_file_jump)
            self.unknown_0x0C   = rw.rw_uint32(self.unknown_0x0C)
            
            if self.file_size == 0xFFFFFFFF or self.next_file_jump == 0xFFFFFFFF:
                return
            
            if rw.mode() == "read":
                file_blob = rw.rw_bytestring(None, self.file_size)
                rw.align(rw.tell(), 0x10)
                self.__parse_file(file_blob)
            else:
                file_blob = b''
                file_blob = self.__unparse_file(file_blob)
                rw.rw_bytestring(file_blob, self.file_size)
                rw.align(rw.tell(), 0x10)

        # Implement below methods on the Interface
        def __handle_file_parse(self, rw, blob):
            rw.bytestream = io.BytesIO(blob)

            if rw.mode() == "read":
                magic = rw.peek_bytestring(4)
                nm = self.name_buffer.split(b'\x00')[0].decode('ascii')
                ext = nm.rsplit('.', 1)[-1]
                if ext == "mds":
                    self.file = MDSBinary()
                elif ext == "bbp":
                    self.file = BBPBinary()
                elif ext == "wgt":
                    self.file = WGTBinary()
                elif ext == "mot":
                    self.file = MOTBinary()
                elif ext == "cfg":
                    self.file = TextBinary()
                elif ext == "img":
                    if magic == b"IMG\x00":
                        self.file = IMGBinary()
                    elif magic == b"IM2\x00":
                        self.file = IM2Binary()
                    else:
                        raise NotImplementedError(f"Unknown texture type: {magic}")
                elif ext == "clo":
                    self.file = TextBinary()
                elif ext == "chr":
                    self.file = CHRBinary()
                elif ext == "":
                    pass
                else:
                    raise NotImplementedError(f"Unknown file extension '{ext}'")
            
            if self.file is not None:
                self.file = rw.rw_obj(self.file)
            
            if rw.mode() == "read":
                return blob
            else:
                rw.bytestream.seek(0)
                return rw.bytestream.read()
                
        def __parse_file(self, blob):
            return self.__handle_file_parse(Reader(None), blob)
            
        def __unparse_file(self, blob):
            return self.__handle_file_parse(Writer(None), blob)
    