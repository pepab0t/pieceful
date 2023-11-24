class Depends:
    def __init__(self, name: str, component_type: type):
        self.name: str = name
        self.component_type: type = component_type
