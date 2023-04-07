import json

class Token:
    def __init__(self, name, range, definition, reference, uri,children):
        self.name = name
        self.range = range
        self.definition = definition
        self.reference = reference
        self.uri = uri
        self.children = children
def analyze_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        json_tree = json.load(f)
        # print(json_tree,' ',type(json_tree))
        tree_info_list = {}
        token_list = []
        traverse_project_tree(json_tree, tree_info_list)
        # print(tree_info_list.keys())
        for file, lsp_tree_info in tree_info_list.items():
            print(file, lsp_tree_info)
            print('lsp_tree_info',type(lsp_tree_info))
            traverse_lsp_info_tree(lsp_tree_info, token_list)
        for item in token_list:
            print('token name:', item.name,' start location:', item.range)
# lsp_tree_info_list stored the information of all java files' lsp output.
def traverse_project_tree(node, lsp_tree_info_list):
    if isinstance(node, dict):
        # if the node is a dictionary, traverse each key-value pair recursively
        for key, value in node.items():
            # print('key', key)
            traverse_project_tree(value, lsp_tree_info_list)
            if key=='lspTreeInfo' and len(value)!=0:
                lsp_tree_info_list[node['name']] = value[0];
    elif isinstance(node, list):
        # if the node is a list, traverse each item in the list recursively
        for item in node:
            traverse_project_tree(item, lsp_tree_info_list)
    # else:
    #     # if the node is a leaf node, print its value
    #     print(node)
def traverse_lsp_info_tree(node,  tokenList):
    # if the node is a dictionary, traverse each key-value pair recursively
    # print('node',type(node))
    token = Token(node['name'],node['startLoacation'],node['definition'],node['reference'],node['uri'],node['children'])
    tokenList.append(token)
    for item in node['children']:
        traverse_lsp_info_tree(item, tokenList)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    analyze_json("Json/tree_info.json")
