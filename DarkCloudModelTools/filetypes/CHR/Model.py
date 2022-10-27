from .CHRInterface import CHRInterface
from ..CFG.CFGInterface import CFGInterface

class Model:
    def __init__(self):
        self.submodels = []

    @classmethod
    def from_chr(cls, chr_interface):
        instance = cls()
        
        # Locate CFG files
        cfgs = []
        for nm, file in chr_interface.files.items():
            if type(file) == CFGInterface:
                cfgs.append(file)
        
        for cfg in cfgs:
            submodel = SubModel()
            submodel.mds = chr_interface.files[cfg.mds]
            submodel.bbp = chr_interface.files[cfg.bbp]
            submodel.wgt = chr_interface.files[cfg.wgt]
            submodel.mot = chr_interface.files[cfg.mot]
            submodel.imgs = [chr_interface.files[img_name] for img_name in cfg.imgs]
            instance.submodels.append(submodel)
        
        return instance
        
    def to_chr(self):
        raise NotImplementedError

class SubModel:
    def __init__(self):
        self.mds = None
        self.bbp = None
        self.wgt = None
        self.mot = None
        self.imgs = []
