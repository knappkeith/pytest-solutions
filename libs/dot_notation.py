def dot_notation_get(json_obj, mapping):
    mapped_obj = json_obj
    for i in mapping.split("."):
        mapped_obj = mapped_obj[i]
    return mapped_obj

def dot_notation_set(json_obj, mapping, value):
    array_map = mapping.split(".")
    mapped_obj = json_obj
    for index, i in enumerate(array_map):
        try:
            mapped_obj = mapped_obj[i]
        except KeyError:
            if index == len(array_map) - 1:
                mapped_obj[i] = value
            else:
                mapped_obj[i] = {}
            mapped_obj = mapped_obj[i]
