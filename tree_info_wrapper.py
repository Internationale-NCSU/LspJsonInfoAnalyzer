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
    def __init__(self, uuid, node_type_, name, path,
                 reference_tree_nodes, definition_tree_node, children_tree_nodes,
                 parent_tree_node):
        self.uuid = uuid,
        self.node_type = node_type_
        self.name = name
        self.path = path
        self.reference_tree_nodes = reference_tree_nodes  # could be null if type is DIRECTORY/FILE
        self.definition_tree_node = definition_tree_node  # could be null if type is DIRECTORY/FILE
        self.parent_tree_node = parent_tree_node
        self.children_tree_nodes = children_tree_nodes


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
        node = tree_node(json_data['uuid'], node_type_, json_data['name'], path, json_data['reference_uuid'],
                         json_data['definition_uuid'], [], [])
        uuid_tree_node_mapping[json_data['uuid']] = node
        if len(json_data['children']) != 0:
            for item in json_data['children']:
                node.children_tree_nodes.append(create_lsp_info_node(item))
        return node

    def create_node(json_data):
        # project tree info directory node:
        if json_data['isDir']:
            path = path_mapping[json_data['mappingNum']]
            node = tree_node(json_data['uuid'], node_type.DIRECTORY, json_data['name'], path, [], [], [], [])
            uuid_tree_node_mapping[json_data['uuid']] = node
            if len(json_data['childrenDir']) != 0:
                for item in json_data['childrenDir']:
                    node.children_tree_nodes.append(create_node(item))
        # project tree info (java) file node:
        else:
            path = path_mapping[json_data['mappingNum']]
            node = tree_node(json_data['uuid'], node_type.FILE, json_data['name'], path, [], [], [], [])
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


def traverse_tree(root: tree_node,uuid_tree_node_mapping):
    reference_nodes = []
    print('token name:', root.name, ', uuid:', root.uuid, ', ')
    for uuid in root.reference_tree_nodes:
        print('reference_uuid:', uuid)
        if uuid in uuid_tree_node_mapping.keys():
            reference_nodes.append(uuid_tree_node_mapping[uuid])
    if len(reference_nodes)!=0:
        print('===== reference node =====')
        for item in reference_nodes:
            print(item.name,' ',item.uuid)
        print("======definition node=======")
        print(uuid_tree_node_mapping[root.definition_tree_node].name)
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


if __name__ == "__main__":
    generate_lsp_info_tree('Json/tree_info.json')
