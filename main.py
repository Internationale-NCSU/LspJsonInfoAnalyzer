import json_wrapper as jw

json_wrapper = jw.json_wrapper('Json/tree_info.json')

for item in json_wrapper.result:
    if type(item)==jw.json_wrapper.Token:
        print('token:', item.name)
    elif type(item)==jw.json_wrapper.function:
        print('func:', item.name)
        for token in item.token:
            print('     token:', token.name)
            print('     reference_uuid:', token.reference_uuid)