import sys, inspect

def is_mod_function(mod, func):
    return inspect.isfunction(func) and inspect.getmodule(func) == mod

def get_functions(mod):
    return [func for func in mod.__dict__.itervalues() 
            if is_mod_function(mod, func)]


def list_functions(mod):
    return [func.__name__ for func in mod.__dict__.itervalues() 
            if is_mod_function(mod, func)]
