#工具类
index_dict ={
    "0":"first",
    "1":"second",
    "2":"third"
}


def to_index_class(index):

    for key,value in index_dict.items():
        if str(index) == key:
            return value
    return ""