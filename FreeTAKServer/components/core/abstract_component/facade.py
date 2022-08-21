from digitalpy.model.node import Node
from digitalpy.model.load_configuration import LoadConfiguration
from digitalpy.config.impl.inifile_configuration import InifileConfiguration
from digitalpy.routing.impl.default_action_mapper import DefaultActionMapper
from digitalpy.core.object_factory import ObjectFactory

class Facade:
    
    def __init__(self, config_path_template, domain, action_mapping_path, logger, type_mapping = None):
        self.config_loader = LoadConfiguration(config_path_template)
        self.domain = domain
        self.action_mapping_path = action_mapping_path
        self.logger = logger
        self.type_mapping = type_mapping

    def initialize(self, request, response):
        self.request = request
        self.response = response
    
    def execute(self, method=None):
        self.request.set_value('logger', self.logger.get_logger())
        self.request.set_value('facade', self)
        getattr(self, method)()
    
    def get_logs(self):
        self.logger.get_logs()
    
    def discover(self):
        pass
    
    def register(self, config: InifileConfiguration):
        config.add_configuration(self.action_mapping_path)
        self._register_type_mapping()
        
    def _register_type_mapping(self):
        """any component may or may not have a type mapping defined, 
        if it does then it should be registered"""
        if self.type_mapping is not None:
            request = ObjectFactory.get_new_instance('request')
            request.set_action("RegisterMachineToHumanMapping")
            request.set_value("machine_to_human_mapping", self.type_mapping)
                        
            actionmapper = ObjectFactory.get_instance('actionMapper')
            response = ObjectFactory.get_new_instance('response')
            actionmapper.process_action(request, response)
            
            request = ObjectFactory.get_new_instance('request')
            request.set_action("RegisterHumanToMachineMapping")
            # reverse the mapping and save the reversed mapping
            request.set_value("human_to_machine_mapping", {k: v for v, k in self.type_mapping.items()})
                        
            actionmapper = ObjectFactory.get_instance('actionMapper')
            response = ObjectFactory.get_new_instance('response')
            actionmapper.process_action(request, response)
        
    def get_metrics(self):
        pass
    
    def get_health(self):
        pass
    
    def accept_visitor(self, node: Node, visitor):
        return node.accept_visitor(visitor)
    
    def add_child(self, node: Node, child):
        return node.add_child(child)

    def create_node(self, message_type, object_class_name):
        configuration = self.config_loader.find_configuration(message_type)
        object_class = getattr(self.domain, object_class_name)
        object_class_instance = object_class(configuration, self.domain)
        return object_class_instance
        
    def delete_child(self, node: Node, child_id):
        return node.delete_child(child_id)

    def get_children_ex(self, id, node: Node, children_type, values, properties, use_regex=True):
        return node.get_children_ex(id, node, children_type, values, properties, use_regex)
        
    def get_first_child(self, node: Node, child_type, values, properties, use_regex=True):
        return node.get_first_child(child_type, values, properties, use_regex)
    
    def get_next_sibling(self, node):
        return node.get_next_sibling()

    def get_num_children(self, node: Node, children_type = None):
        return node.get_num_children(children_type)
    
    def get_num_parents(self, node: Node, parent_types = None):
        return node.get_num_parents(parent_types)
    
    def get_previous_sibling(self, node: Node):
        return node.get_previous_sibling()
    
    def get_parent(self, node: Node):
        return node.get_parent()