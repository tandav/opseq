class AppendOp:
    def __init__(self, options):
        self.options = options
    
    def __call__(self, seq):
        for op in self.options:
            yield seq + (op,)
