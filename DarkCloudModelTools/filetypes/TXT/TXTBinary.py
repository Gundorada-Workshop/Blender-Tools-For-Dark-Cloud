from ...serialisation.Serializable import Serializable

class TextBinary(Serializable):
    def __init__(self, context=None):
        super().__init__(context)
        
        self.text = []
        
    def __repr__(self):
        return f"[Text] {self.text}"
    
    def read_write(self, rw):
        self.text = rw.rw_str(self.text, length=-1, encoding="sjis")
