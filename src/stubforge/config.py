from collections import OrderedDict
from typing import TypeAlias, TypedDict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from stubforge.stubforge_types import *


@dataclass
class Settings:
    '''
    Object containing user settings for stubforge
    '''
    trust_keyvalue_consistency: bool 
    max_recursion_depth: int 
    force_rewrite: bool 
    trust_list_homogeneity: bool
    dict_probe_policies: list[DictProbePolicy] 

    @property
    def raise_keyvalue_inconsistency(self):
        return self._raise_keyvalue_inconsistency

    @raise_keyvalue_inconsistency.setter
    def raise_keyvalue_inconsistency(self, value):
        if self.trust_keyvalue_consistency == True:
            raise AttributeError("Cannot raise inconsistency warning if consitency is trusted")
        self._raise_keyvalue_inconsistency: bool = value


