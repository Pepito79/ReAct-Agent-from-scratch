from typing import get_type_hints,Callable
import inspect

def extract_params_types(func: Callable) -> dict[str, str]:
    """Extract params and their type from a function

    Args:
        func (Callable): the function

    Returns:
        dict[str, str]
    """
    
    types_resolus = get_type_hints(func)
    signature = inspect.signature(func)
    resultat = {}
    
    for nom_param in signature.parameters:
        type_obj = types_resolus.get(nom_param, signature.parameters[nom_param].annotation)        
        if type_obj is inspect._empty:
            type_str = "Any"  
        elif hasattr(type_obj, "__name__"):
            type_str = type_obj.__name__  
        else:
            type_str = str(type_obj)  
               
        resultat[nom_param] = type_str
        
    return resultat