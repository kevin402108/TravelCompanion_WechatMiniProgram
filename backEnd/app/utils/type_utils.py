from typing import Any , Union , List , Dict , Tuple

# === 通用数据类型基础校验 ===
def is_none(obj: object) -> bool:
    """检查对象是否为None"""
    return obj is None

def is_not_none(obj: object) -> bool:
    """检查对象是否非None"""
    return obj is not None

def is_correct_type( obj: Any , expected_type: Union[type, tuple ] ) -> bool:
    """通用类型校验（自动排除 None）"""
    return obj is not None and isinstance(obj, expected_type)

# === 常用数据类型基础校验 ===
def is_int(obj: Any) -> bool:
    """检查是否为 int（排除 bool）"""
    return is_correct_type(obj, int) and not isinstance(obj, bool)

def is_str(obj: Any) -> bool:
    """检查是否为 str"""
    return is_correct_type(obj, str)

def is_float(obj: Any) -> bool:
    """检查是否为 float"""
    return is_correct_type(obj, float)

def is_bool(obj: Any) -> bool:
    """检查是否为 bool"""
    return is_correct_type(obj, bool)

def is_type_of_list(obj: Any) -> bool:
    """检查是否为 list"""
    return is_correct_type(obj,list)

def is_type_of_tuple(obj: Any) -> bool:
    """检查是否为 tuple"""
    return is_correct_type(obj,tuple)

def is_type_of_dict(obj: Any) -> bool:
    """检查是否为 dict"""
    return is_correct_type(obj,dict)

def is_type_of_set(obj: Any) -> bool:
    """检查是否为 set"""
    return is_correct_type(obj,set)

# === 包含元素类型校验的容器类型校验（常用组合）===
def is_type_of_list_of_str(lst: List[Any]) -> bool:
    """检查是否为 List[str]（允许空列表）"""
    if not is_type_of_list(lst):
        return False
    return all(is_correct_type(item,str) for item in lst)

def is_type_of_list_of_int(lst: List[Any]) -> bool:
    """检查是否为 List[int]（排除 bool）"""
    if not is_type_of_list(lst):
        return False
    return all(is_correct_type(item,int) and not isinstance(item,bool ) for item in lst)

def is_type_of_dict_str_to_str(d: Dict[Any, Any]) -> bool:
    """检查是否为 Dict[str, str]"""
    if not is_type_of_dict(d):
        return False
    return all(
        is_correct_type( k , str ) and is_correct_type( v , str )
        for k, v in d.items()
    )

def is_type_of_tuple_of_two_ints(t: Tuple[Any, ...]) -> bool:
    """检查是否为 Tuple[int, int]（长度严格为 2）"""
    if not is_type_of_tuple(t) or len(t) != 2:
        return False
    return is_correct_type(t[0] , int) and is_correct_type( t[1] , int ) and \
           not isinstance(t[0], bool) and not isinstance(t[1], bool)
