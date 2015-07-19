'''
entities.py: basic geometric primitives

Design intent: only store references to vertex indices and pass the vertex
               array back to functions that require it. 
               This keeps all vertices in one external list.
'''

import numpy as np

from .constants import *
from .arc       import discretize_arc, arc_center
from .bezier    import discretize_bezier

from ..points   import unitize
from ..util     import replace_references

_HASH_LENGTH = 5

class Entity:
    def __init__(self, 
                 points, 
                 closed = False):
        self.points = np.array(points)
        self.closed = closed
        
    @property
    def _class_id(self):
        '''
        Return an integer that is unique to the class type.
        Note that this implementation will fail if a class is defined
        that starts with the same letter as an existing class. 
        Since this function is called a lot, it is a tradeoff between 
        speed and robustness where speed won. 
        '''
        return ord(self.__class__.__name__[0])

    def hash(self):
        '''
        Returns a string unique to the entity.
        If two identical entities exist, they can be removed
        by comparing the string returned by this function.
        '''
        hash = np.zeros(_HASH_LENGTH, dtype=np.int)
        hash[-2:] = self._class_id, int(self.closed)
        hash[0:len(self.points)] = np.sort(self.points)
        return hash
        
    def to_dict(self):
        '''
        Returns a dictionary with all of the information about the entity. 
        '''
        return {'type'  : self.__class__.__name__, 
                'points': self.points.tolist(),
                'closed': self.closed}
                
    def rereference(self, replacement):
        '''
        Given a replacement dictionary, change points to reflect the dictionary.
        eg, if replacement = {0:107}, self.points = [0,1902] becomes [107, 1902]
        '''
        self.points = replace_references(self.points, replacement)
        
    def nodes(self):
        '''
        Returns an (n,2) list of nodes, or vertices on the path.
        Note that this generic class function assumes that all of the reference 
        points are on the path, which is true for lines and three point arcs. 
        If you were to define another class where that wasn't the case
        (for example, the control points of a bezier curve), 
        you would need to implement an entity- specific version of this function.
        
        The purpose of having a list of nodes is so that they can then be added 
        as edges to a graph, so we can use functions to check connectivity, 
        extract paths, etc.  
        
        The slicing on this function is essentially just tiling points
        so the first and last vertices aren't repeated. Example:
        
        self.points = [0,1,2]
        returns:      [[0,1], [1,2]]
        '''
        return np.column_stack((self.points,
                                self.points)).reshape(-1)[1:-1].reshape((-1,2))
                       
    def end_points(self):
        '''
        Returns the first and last points. Also note that if you
        define a new entity class where the first and last vertices
        in self.points aren't the endpoints of the curve you need to 
        implement this function for your class.
        
        self.points = [0,1,2]
        returns:      [0,2]
        '''
        return self.points[[0,-1]]
            
class Arc(Entity):
    def discrete(self, vertices):
        return discretize_arc(vertices[self.points], 
                              close = self.closed)
                              
    def center(self, vertices):
        return arc_center(vertices[self.points])
                
    def tangents(self, vertices):
        return arc_tangents(vertices[self.points])

class Line(Entity):
    def discrete(self, vertices):
        return vertices[[self.points]]

class Bezier(Entity):
    def discrete(self, vertices):
        return discretize_bezier(vertices[self.points])

    def nodes(self):
        return [[self.points[0], 
                 self.points[-1]]]
