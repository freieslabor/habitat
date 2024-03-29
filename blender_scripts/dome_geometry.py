
# script to calc/plan bars of habitat roof dome.

# Blender 2.80 !!!

# not yet figured out how to make a script or plugin.
# copy/paste this whole file into the blender console.




import bpy
import os
import os.path
import math
import mathutils
import mathutils.geometry




NUMCOL = 10				# number of columns (corners)
RADIUS = 2.5*0.98			# radius to corners

SMALLER_RAD_FAC = 0.6	# factor to scale middle-ring down compared to base-ring.


# calc all vertexes and normals.
# vertexes.
HEIGHT_DOME = RADIUS*0.6
HEIGHT_INT_RING = HEIGHT_DOME*math.sqrt(0.5)


ROOM_HEIGHT = 2.0		# for elevating above the ground.

# bar dimensions
BAR_W = 0.04
BAR_T = 0.028
BAR_END_TAP = 0.09

BEND_LENGTH = 0.1		# length of metal bent over. Distance from crease to screwhole.
BEND_RADIUS = 0.005		# bending radius of the metal parts.


#_msh = bpy.data.meshes.new('einMesh')
#_obj = bpy.data.objects.new('obj111',_msh)

class Plane(object):
	""" Plane type. Cannot find it in blender. Blender MUST have a plane datatype. """
	__slots__ = ('norm','off')
	def __init__(self,arg1,arg2,arg3=None):
		if arg3 is None:
			self._load_from_norm_and_off(arg1,arg2)
		else:
			self._load_from_three_points(arg1,arg2,arg3)
	def _load_from_norm_and_off(self,norm,norm_off_factor):
		if not isinstance(norm,mathutils.Vector):
			raise AttributeError("arg1 must be a vector. The plane normal.")
		if (not isinstance(norm_off_factor,float)) and (not isinstance(norm_off_factor,int)):
			raise AttributeError("arg2 must be a number. The plane offset from zero.")
		lo = norm.length
		self.off = float(norm_off_factor)*lo
		self.norm = norm.copy()
		self.norm.normalize()
	def _load_from_three_points(self,p1,p2,p3):
		for p in (p1,p2,p3):
			if not isinstance(p,mathutils.Vector):
				raise AttributeError("all args must be vectors. The plane normal.")
			norm = (p2-p1).cross((p3-p1))
			norm.normalize()
			off = norm.dot(p1)
			self._load_from_norm_and_off(norm,off)
	def intersect(self,other):
		"""
			Find intersection corner line.
			wrapper for blender  mathutils.geometry.intersect_plane_plane
		"""
		if not isinstance(other,Plane):
			raise AttributeError("arg must be a Plane.")
		point,cutdir = mathutils.geometry.intersect_plane_plane(
				self.norm*self.off,
				self.norm,
				other.norm*other.off,
				other.norm
		)
		# find angle
		_v = self.norm.dot(other.norm)
		if _v<0.8:
			angle = math.acos(_v)
		else:
			_v = self.norm.cross(other.norm).length
			angle = math.asin(_v)
		return (point,cutdir,angle)

#dummies to play
#p1 = Plane(mathutils.Vector((1,1,0)),1)
#p2 = Plane(mathutils.Vector((-2,2,0)),2)
#
#p1.intersect(p2)

v1 = mathutils.Vector((1,2,3))
v2 = mathutils.Vector((1,2,30))
v3 = mathutils.Vector((4,5,6))
p = Plane(v1,v2,v3)

def dirvecs_to_rotmat(forwardvector,upwardvector):
	""" convert dir-vectors to matrix. Assume foward is Y+, Z is up to sky. """
	fwd = forwardvector.copy()
	upw = upwardvector.copy()
	fwd.normalize()				# vector to length 1.
	upw -= fwd.dot(upw)*fwd		# remove component parallel to fwd, which causes dot-prod to be non-zero. Thus fix to be orthogonal.
	upw.normalize()				# after fixing, normalize to 1.
	rgt = fwd.cross(upw)		# find third vector from the two using crossproduct.
	# use the three as column-vectors and build the rotation matrix.
	return mathutils.Matrix((mathutils.Vector((rgt.x,fwd.x,upw.x)),mathutils.Vector((rgt.y,fwd.y,upw.y)),mathutils.Vector((rgt.z,fwd.z,upw.z))))

def dirvecs_to_rotquat(forwardvector,upwardvector):
	""" convert dir-vectors to quat. Assume foward is Y+, Z is up to sky. """
	m = dirvecs_to_rotmat(forwardvector,upwardvector)
	return m.to_quaternion()

def upvec_to_rotmat(upwardvector):
	""" convert upward-vec to one possible rot-matrix """
	upw = upwardvector.copy()
	upw.normalize()
	# find any orthogonal vector: Drop smallest component, swap other two, negate one of them.
	if upw.x*upw.x < upw.y*upw.y and upw.x*upw.x < upw.z*upw.z :
		fwd = mathutils.Vector((0.0,upw.z,-upw.y))
	elif upw.y*upw.y < upw.z*upw.z :
		fwd = mathutils.Vector((upw.z,0.0,-upw.x))
	else:
		fwd = mathutils.Vector((upw.y,-upw.x,0.0))
	return dirvecs_to_rotmat(fwd,upwardvector)

def upvec_to_rotquat(upwardvector):
	""" convert upward-vec to one possible rot-quat """
	m = upvec_to_rotmat(upwardvector)
	return m.to_quaternion()

def calc_angle(vec1,vec2,axis=None):
	vec1.copy()
	vec2.copy()
	vec1.normalize()
	vec2.normalize()
	if axis is not None:
		m = dirvecs_to_rotmat(axis,vec1)
		m.transpose()	# invert
		# now apply vec2 to get it into XY plane
		v2 = m @ vec2
		#print(m)
		#print(m@axis)
		#print(m@vec1)
		#print(m@vec2)
		angle = math.atan2(v2.x,v2.z)
	else:
		_val = vec1.dot(vec2)
		if _val<0.707:
			angle = math.acos(_val)
		else:
			_val = vec1.cross(vec2).length
			angle = math.asin(_val)
	return angle


verts = [None] * (NUMCOL*3+1)
norms = verts[:]
# calc location of all vertices
for i in range(NUMCOL):
	a0 = math.pi*2.0*(i+0.0)/NUMCOL
	a1 = math.pi*2.0*(i+0.5)/NUMCOL
	# lower ones
	v = mathutils.Vector(( RADIUS*math.cos(a0) , RADIUS*math.sin(a0) , 0.0 ))
	verts[i] = v
	# ground points
	v = mathutils.Vector(( RADIUS*math.cos(a1) , RADIUS*math.sin(a1) , -ROOM_HEIGHT ))
	verts[i+NUMCOL*2] = v
	v = mathutils.Vector(( SMALLER_RAD_FAC*RADIUS*math.cos(a1) , SMALLER_RAD_FAC*RADIUS*math.sin(a1) , HEIGHT_INT_RING ))
	# middle ring
	verts[i+NUMCOL] = v

# last vertex on top
v = mathutils.Vector(( 0.0 , 0.0 , HEIGHT_DOME ))
verts[NUMCOL*3] = v

for v in verts:
	print("  (%6.2f/%6.2f/%6.2f)"%(v.x,v.y,v.z))

#help-func to get 'up' vertor for a vector, which is 90 deg to input vector, but mostly up.
def up_vector(v):
	# make orthogonal in plane by zeroing z and swapping xy.
	v2 = mathutils.Vector(( v.y , -v.x , 0.0 ))
	res = v.cross(v2)
	res.normalize()
	return res

# calc normals.
# for lower circle, normals are straight out.
# for middle circle, normals are mean of the dirs of the three bars at the point.
for i in range(NUMCOL):
	v = verts[i].copy()
	v.normalize()
	# tilt up normal of outer points. Otherwise there are too high angles of 43 deg.
	tiltup_deg = 20
	v.z = math.tan(tiltup_deg*math.pi/180.0)
	v.normalize()
	norms[i] = v
	#edges of one middle-ring vertex
	sv1 = verts[i+NUMCOL] - verts[i]
	sv2 = verts[i+NUMCOL] - verts[(i+1)%NUMCOL]
	sv3 = verts[i+NUMCOL] - verts[3*NUMCOL]
	sv1.normalize()
	sv2.normalize()
	sv3.normalize()
	p = Plane(sv1,sv2,sv3)
	n = p.norm
#	n = sv1+sv2+sv3
#	n.normalize()
	norms[i+NUMCOL] = n
	# ground verts just point outside
	v = verts[i+2*NUMCOL].copy()
	v.z=0
	v.normalize()
	norms[i+2*NUMCOL] = v

norms[3*NUMCOL] = mathutils.Vector(( 0,0,1 ))

for v in norms:
	print("  (%6.2f/%6.2f/%6.2f)"%(v.x,v.y,v.z))

# calc edges (beams) now.
# try to rotate them so the middle point is pointing mostly upward.
# first fill in tuples:  (index of vert0,index of vert1,upward-vector)

edges = list()

up = mathutils.Vector(( 0,0,1 ))
for i in range(NUMCOL):
	# outer edge
	idx0 = i
	idx1 = (i+1)%NUMCOL
	v0 = verts[idx0]
	v1 = verts[idx1]
	edges.append( (idx0,idx1,(v0+v1)) )
	# middle ring
	idx0 = NUMCOL+i
	idx1 = NUMCOL+(i+1)%NUMCOL
	v0 = verts[idx0]
	v1 = verts[idx1]
	edges.append( (idx0,idx1,up) )
	# lower zigzag
	idx0 = i
	idx1 = NUMCOL+i
	v0 = verts[idx0]
	v1 = verts[idx1]
	edges.append( (idx0,idx1,up) )
	idx0 = (i+1)%NUMCOL
	v0 = verts[idx0]
	edges.append( (idx0,idx1,up) )
	# upper star
	idx0 = NUMCOL+i
	idx1 = NUMCOL*3
	v0 = verts[idx0]
	v1 = verts[idx1]
	edges.append( (idx0,idx1,up) )
	# wall posts
	idx0 = i
	idx1 = NUMCOL*2+i
	v0 = verts[idx0]
	v1 = verts[idx1]
	edges.append( (idx0,idx1,(v0+v1)) )
	idx0 = (i+1)%NUMCOL
	v0 = verts[idx0]
	edges.append( (idx0,idx1,(v0+v1)) )


# process edges to correct orientation of the 'up' vector to be really orthogonal.
edges_n = list()
for idx0,idx1,tup in edges:
	v0 = verts[idx0]
	v1 = verts[idx1]
	edir = (v1-v0).copy()
	edir.normalize()
	n0 = norms[idx0].copy()
	n1 = norms[idx1].copy()
	# shift norms to make them vertical to direction of bar.
	n0 -= edir.dot(n0)*edir
	n1 -= edir.dot(n1)*edir
	n0.normalize()
	n1.normalize()
	# pick average of these as 'up' for the bar.
	up = 0.5*(n0+n1)
	edges_n.append((idx0,idx1,up))

edges = edges_n
del(edges_n)


def bend_shortening(angle):
	"""
		Calc how much a bar is shortened by bending over the ends.
		angle is in radians.
	"""
	# curved-len = bendrad * angle
	bowlen = BEND_RADIUS*angle
	backoff = BEND_LENGTH + 0.5*bowlen
	downstraight = BEND_LENGTH - 0.5*bowlen
	add_length = (0-backoff) + BEND_RADIUS*math.sin(angle) + math.cos(angle)*downstraight
	return -add_length





sumlength = 0.0

# calc and print the angles of the connecting metal pieces.
for i in range(len(edges)):
	idx0,idx1,norm = edges[i]
	v0 = verts[idx0]
	v1 = verts[idx1]
	leng = (v1-v0).length
	## plane for bar
	#p1 = Plane(norm,norm.dot(v0))
	## plane for screw A
	#pA = Plane(norms[idx0],norms[idx0].dot(v0))
	## plane for screw B
	#pB = Plane(norms[idx1],norms[idx1].dot(v1))
	#cutpointA,cutdirA,cutangleA = p1.intersect(pA)
	#cutpointB,cutdirB,cutangleB = p1.intersect(pB)
	#cutangleA *= (180/math.pi)
	#cutangleB *= (180/math.pi)
	# get edge-dir and orth-corrected normals.
	edir = (v1-v0).copy() ; edir.normalize()
	n0 = norms[idx0].copy()
	n1 = norms[idx1].copy()
	n0 -= edir.dot(n0)*edir
	n1 -= edir.dot(n1)*edir
	n0.normalize()
	n1.normalize()
	twistangleA = calc_angle(norm,n0,edir)
	twistangleB = calc_angle(norm,n1,edir*-1.0)
	bendangleA = calc_angle(n0,norms[idx0])
	bendangleB = calc_angle(n1,norms[idx1])
	shorteningA = bend_shortening(bendangleA)
	shorteningB = bend_shortening(bendangleB)
	fact = 180.0/math.pi
	twistangleA *= fact
	twistangleB *= fact
	bendangleA  *= fact
	bendangleB  *= fact
	print("  bar #%2d   %6.3fm   tw%6.2fdeg    bdA%5.2fdeg   bdB %5.2fdeg"%(i,leng,twistangleA+twistangleB,bendangleA,bendangleB))
	sumlength += leng

print ("total length of %d bars: %.2f"%(len(edges),sumlength))
# here I have:

# list 'verts' with the Vectors of the cornerpoints. These are the screws
# list 'norms' with the normals, indicating the direction of the screws on the corner points.
# list 'edges' with 3-tuples with start-vector-index, end-vector-index, 'upward' vector.

# strategy to calculate angles:
# find plane of bar.
# find plane orthogonally to screw
# find cutting edge between these planes.
# find angle of cut of the planes    (1)
# find angle of cutting edge relaive to bar-length vector. (2)


# temporary. generate simplified bars.

def gencube(name,lx,ly,lz):
	lx*=0.5
	ly*=0.5
	lz*=0.5
	verts = ((-lx,-ly,-lz),(lx,-ly,-lz),(-lx,ly,-lz),(lx,ly,-lz),(-lx,-ly,lz),(lx,-ly,lz),(-lx,ly,lz),(lx,ly,lz))
	edgs = ()
	facs = ((0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6),(2,3,1,0),(4,5,7,6))
	# now create it.
	_msh = bpy.data.meshes.new('mesh')
	_obj = bpy.data.objects.new(name,_msh)
	_msh.from_pydata(verts,edgs,facs)
	_msh.validate()
	bpy.context.scene.collection.objects.link(_obj)
	_obj.rotation_mode = 'QUATERNION'
	return _obj

def genscrewline(name,l):
	l*=0.5
	verts = ((0,0,-l),(0,0,l))
	edgs = ((0,1),)
	facs = ()
	# now create it.
	_msh = bpy.data.meshes.new('linemesh')
	_obj = bpy.data.objects.new(name,_msh)
	_msh.from_pydata(verts,edgs,facs)
	_msh.validate()
	bpy.context.scene.collection.objects.link(_obj)
	_obj.rotation_mode = 'QUATERNION'
	return _obj



# bar dimensions
#BAR_W  0.04     * 4
#BAR_T  0.028     * 4
#BAR_END_TAP  0.09     * 4

# one parent object for easier handling.
obj_dome = bpy.data.objects.new('dome',None)
bpy.context.scene.collection.objects.link(obj_dome)

# generate cubes for blender visualization
for i in range(len(edges)):
	idx0,idx1,upw = edges[i]
	v0 = verts[idx0]
	v1 = verts[idx1]
	leng = (v1-v0).length
	obj = gencube("bar%02d"%i,BAR_W,leng,BAR_T)
	obj.location = (v0+v1)*0.5
	obj.rotation_mode = 'QUATERNION'
	q = dirvecs_to_rotquat(v1-v0,upw)
	obj.rotation_quaternion = q
	obj.scale = mathutils.Vector((1,1,1))
	obj.parent = obj_dome

# generate lines to show orientation of screws.
for i in range(len(verts)):
	obj = genscrewline("screw%02d"%i,0.3)
	obj.location = verts[i]
	q = upvec_to_rotquat(norms[i])
	obj.rotation_quaternion = q
	obj.scale = mathutils.Vector((1,1,1))
	obj.parent = obj_dome

#obj_dome.location = mathutils.Vector((0,0,ROOM_HEIGHT))

# TODO:
#   lots
#   bars are middle-centered. should be oriented around top of bar.
#   bent sheetmetal ends are not modelled, offset of bent ends is not considered.

#for i in range(0,91,5):
#	ang = math.pi*i/180.0
#	print("%2d deg  ->  %8.2f cm"%( i , 100.0*bend_shortening(ang) ))


def calc_length_with_bent_ends(edge_index):
	""" calc len of bar with consideration of the bends. """
	idx0,idx1,enorm = edges[edge_index]
	v0 = verts[idx0]
	v1 = verts[idx1]




