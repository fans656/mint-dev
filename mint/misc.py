def new_obj_index(o, indexes={}):
    cls = type(o)
    if cls not in indexes:
        indexes[cls] = 0
    else:
        indexes[cls] += 1
    return indexes[cls]
