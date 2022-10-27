import re
from ..TXT.TXTBinary import TextBinary


class CFGInterface:
    line_parser = re.compile("[^\\s\"]+|\"[^\"]*\"")
    
    def __init__(self):
        self.imgs = []
        self.mds = None
        self.bbp = None
        self.wgt = None
        self.mot = None

    #################################
    # Data Transformation Functions #
    #################################
    @classmethod
    def from_file(cls, filepath):
        binary = TextBinary()
        binary.read(filepath)
        return cls.from_binary(binary.file)
        
    def to_file(self, filepath):
        binary = self.to_binary()
        binary.write(filepath)

        
    @classmethod
    def from_binary(cls, binary):
        instance = cls()
        for line in binary.text.split('\n'):
            # Parser has a bug where quotes start new matches...
            # Need to fix
            line, _, comment = line.partition("//")
            line = cls.line_parser.findall(line)
            
            if len(line):
                if line[0] == "IMG":
                    idx = int(line[1].rstrip(","))
                    if len(instance.imgs) < (idx + 1):
                        instance.imgs.extend(None for _ in range(idx + 1 - len(instance.imgs)))
                    instance.imgs[idx] = line[2][1:-1]
                elif line[0] == "MODEL":
                    instance.mds = line[1][1:-1]
                elif line[0] == "MOTION":
                    instance.mot = line[2][1:-1]
                    instance.bbp = line[4][1:-1]
                    instance.wgt = line[6][1:-1]
        return instance
        
    def to_binary(self):
        raise NotImplementedError