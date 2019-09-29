
# just some code to play around with blender geometry generation.
# use by copy-paste into blenders python-console 

# Blender 2.80 !!!


import bpy
import os
import os.path
import math
import mathutils
import mathutils.geometry



_msh = bpy.data.meshes.new('einMesh')
_obj = bpy.data.objects.new('obj111',_msh)


_verts = [(-2,-2,-2),(2,-2,-2),(0,2,-2),(0,0,2)]
_verts = [(0,0,0),(1,0,0),(0,1,0),(0,0,1)]
_edgs = [] # [(0,1),(1,2),(2,0),(0,3),(1,3),(2,3)]
_fcs = [(0,2,1),(0,1,3),(1,2,3),(2,0,3)]

_verts = [(-1,-1,0),(-1,1,0),(1,1,0),(1,-1,0),(0,0,2),]
_edgs = []
_fcs = [(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)]

for i in range(len(_verts)):
	v = mathutils.Vector(_verts[i])
	_verts[i] = v

_msh.from_pydata(_verts,_edgs,_fcs)
_msh.validate()
bpy.context.scene.collection.objects.link(_obj)

_obj.rotation_mode = 'QUATERNION'
_obj.rotation_quaternion = mathutils.Quaternion((0.4,0.4,0.4,math.sqrt(1-3*0.16)))
_obj.location = mathutils.Vector((0.1,0.1,0.1))
_obj.scale = mathutils.Vector((0.1,0.1,0.1))


