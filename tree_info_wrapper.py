import copy
from enum import Enum
import json


class node_type(Enum):
    DIRECTORY = 1,
    FILE = 2,
    FUNCTION = 3,
    TOKEN = 4
    UNDEFINED = 5


# path should be gotten from the path_mapping from the mapping_num
class tree_node:
    def __init__(self, node_id: str, node_type_, name, path,
                 reference_tree_nodes, definition_tree_node, children_tree_nodes,
                 parent_tree_node):
        self.uuid = node_id,
        self.node_type = node_type_
        self.name = name
        self.path = path
        self.reference_tree_nodes = reference_tree_nodes  # could be null if type is DIRECTORY/FILE
        self.definition_tree_node = definition_tree_node  # could be null if type is DIRECTORY/FILE
        self.parent_tree_node = parent_tree_node
        self.children_tree_nodes = children_tree_nodes
        self.uuid = self.uuid[0]


def get_mapping_info(json_tree):
    for key, value in json_tree.items():
        if key == 'data':
            data = value[0]
        # elif key == 'forwardMap':
        #     forward_map = {}
        #     for item in value:
        #         forward_map[item[0]] = item[1]
        elif key == 'reverseMap':
            reverse_map = {}
            for item in value:
                reverse_map[item[0]] = item[1]
    return [data, reverse_map]


def wrap_json_to_tree(data, uuid_tree_node_mapping, path_mapping):
    def create_lsp_info_node(json_data):
        # print('lsp tree node name:', json_data['name'])
        path = path_mapping[json_data['mappingNum']]
        node_type_ = node_type.UNDEFINED
        if json_data['type'] == 'func':
            node_type_ = node_type.FUNCTION
        elif json_data['type'] == 'others':
            node_type_ = node_type.TOKEN
        # print('type:', type(json_data['uuid']))

        node = tree_node(node_id=json_data['uuid'], node_type_=node_type_,
                         name=json_data['name'], path=path, reference_tree_nodes=json_data['reference_uuid'],
                         definition_tree_node=json_data['definition_uuid'], children_tree_nodes=[],
                         parent_tree_node=None)
        uuid_tree_node_mapping[json_data['uuid']] = node
        if len(json_data['children']) != 0:
            for item in json_data['children']:
                node.children_tree_nodes.append(create_lsp_info_node(item))
        return node

    def create_node(json_data):
        # project tree info directory node:
        if json_data['isDir']:
            path = path_mapping[json_data['mappingNum']]
            node = tree_node(node_id=json_data['uuid'], node_type_=node_type.DIRECTORY,
                             name=json_data['name'], path=path, reference_tree_nodes=[],
                             definition_tree_node=[], children_tree_nodes=[],
                             parent_tree_node=None)
            uuid_tree_node_mapping[json_data['uuid']] = node
            if len(json_data['childrenDir']) != 0:
                for item in json_data['childrenDir']:
                    node.children_tree_nodes.append(create_node(item))
        # project tree info (java) file node:
        else:
            path = path_mapping[json_data['mappingNum']]
            node = tree_node(node_id=json_data['uuid'], node_type_=node_type.FILE,
                             name=json_data['name'], path=path, reference_tree_nodes=[],
                             definition_tree_node=[], children_tree_nodes=[],
                             parent_tree_node=None)
            uuid_tree_node_mapping['uuid'] = node
            # start to wrap lsp_info:
            node.children_tree_nodes.append(create_lsp_info_node(json_data['lspTreeInfo'][0]))
        return node

    def assign_parent_relation(cur_node: tree_node):
        if len(cur_node.children_tree_nodes) != 0:
            for item in cur_node.children_tree_nodes:
                item.parent_tree_node = cur_node
                assign_parent_relation(item)

    root = create_node(data)
    assign_parent_relation(root)
    return root


def traverse_tree(root: tree_node, uuid_tree_node_mapping):
    reference_nodes = []
    print('----------------------------')
    print('token name:', root.name, ', uuid:', root.uuid)
    for uuid in root.reference_tree_nodes:
        print('reference_uuid:', uuid)
        if uuid in uuid_tree_node_mapping.keys():
            reference_nodes.append(uuid_tree_node_mapping[uuid])

    if len(reference_nodes) != 0:
        print('===== reference node =====')
        for item in reference_nodes:
            print(item.name, ' ', item.uuid)
        print("======definition node=======")
        if root.definition_tree_node!='':
            if root.definition_tree_node in uuid_tree_node_mapping:
                print(uuid_tree_node_mapping[root.definition_tree_node].name, ', ' ,uuid_tree_node_mapping[root.definition_tree_node].uuid)
            else:
                print('Definition of this token is out of project file scope')
        print('----------------------------')
    for node in root.children_tree_nodes:
        traverse_tree(node, uuid_tree_node_mapping)


def generate_lsp_info_tree(path):
    with open(path, 'r', encoding='utf-8') as f:
        json_tree = json.load(f)
        # print(json_tree)
        data, reverse_map = get_mapping_info(json_tree)
        # print('data:', data)
        # print('path_mapping:', reverse_map)
        uuid_tree_node_mapping = {}
        root = wrap_json_to_tree(data, uuid_tree_node_mapping, reverse_map)
        traverse_tree(root, uuid_tree_node_mapping)
        return root


def get_node_by_id(node_id: str, root: tree_node):
    # print('name', root.name, 'id:', root.uuid, ', target_id:', node_id)
    if root.uuid == node_id:
        return root
    elif len(root.children_tree_nodes) != 0:
        for node in root.children_tree_nodes:
            result = get_node_by_id(node_id, node)
            if result is not None:
                return result
    else:
        return None


def get_path_node_to_root(node: tree_node):
    print('path to the root:')
    print('name: ', node.name, ', uuid: ', node.uuid)
    if node.parent_tree_node is not None:
        get_path_node_to_root(node.parent_tree_node)


def proceed_node_by_id(node_id: str, order: str, root: tree_node):
    node = get_node_by_id(node_id, root)

    if order == 'get_node_to_root':
        if node is not None:
            get_path_node_to_root(node)
        else:
            print('node not found.')

    if order == 'get_node_definition':
        if node is not None:
            definition_id = node.definition_tree_node
            if definition_id =='':
                print('Definition of this token is out of project file scope.')
            print('definition_id:', definition_id)
            definition_node = get_node_by_id(definition_id, root)
            if definition_node is None:
                print('definition node not fount.')
            else:
                print('definition name: ', definition_node.name, 'uuid: ', definition_node.uuid)
        else:
            print('node not found.')

    if order == 'print_subtree_by_id':
        node = get_node_by_id(node_id, root)
        print_tree(node)
def print_tree(root:tree_node):
    if root is not None:
        print('node name:',root.name,' uuid: ',root.uuid)
    for node in root.children_tree_nodes:
        print_tree(node)


if __name__ == "__main__":

    lsp_info_tree = generate_lsp_info_tree('Json/tree_info.json')
    while True:
        print('please provide an uuid:')
        uuid = str(input())
        # proceed_node_by_id(uuid, 'get_node_to_root', lsp_info_tree)
        # proceed_node_by_id(uuid, 'get_node_definition', lsp_info_tree)
        proceed_node_by_id(uuid, 'print_subtree_by_id', lsp_info_tree)
