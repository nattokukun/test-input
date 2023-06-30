# -*- coding: utf-8 -*-
#//////////////////////////////////////////////////////////////////////////////
#            const Constant types in Python.
#            https://qiita.com/nadu_festival/items/c507542c11fc0ff32529
#//////////////////////////////////////////////////////////////////////////////
class _consttype:
    class _ConstTypeError(TypeError):
        pass
    def __repr__(self):
        return "Constant type definitions."
    def __setattr__(self, name, value):
        v = self.__dict__.get(name, value)
        if type(v) is not type(value):
            raise self._ConstTypeError("Can't rebind type(v) to type(value)")
            ## raise self._ConstTypeError(f"Can't rebind {type(v)} to {type(value)}")
        self.__dict__[name] = value
    def __del__(self):
        self.__dict__.clear()

import sys
sys.modules[__name__] = _consttype()

pass