import bpy
import collections
import math
import sys

rad = math.radians


#--------------------------------------------------------------------
##class
#--------------------------------------------------------------------
class Term:
    """term for collatz sequence"""
    def __init__(self, n:int=0):
        self.number = n
        self.prev_terms = []

        self.pos = Vec3(0, 0, 0)
        self.rot = Vec3(0, 0, 0)

    def __str__(self):
        return "value: {}, prev: {}".format(self.number, self.prev_terms)


#----------------------------------
class Vec3:
    """3d vector data"""
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "x:{}, y:{}, z:{}".format(self.x, self.y, self.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return self + (-other)

    def mult(self, k):
        self.x *= k
        self.y *= k
        self.z *= k
        return self
    
    def mag(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def heading(self):
        return math.atan2(self.z, self.y)
        
    def rotateXYZ(self, rotVec):
        result = self.rotateX(rotVec.x).rotateY(rotVec.y).rotateZ(rotVec.z)
        return result
    
    def rotateX(self, angle):
        result = Vec3(0,0,0)
        result.x = self.x
        result.y = self.y*math.cos(angle) + self.z*math.sin(angle)
        result.z = -self.y*math.sin(angle) + self.z*math.cos(angle)
        return result
    
    def rotateY(self, angle):
        result = Vec3(0, 0, 0)
        result.x = self.x*math.cos(angle) - self.z*math.sin(angle)
        result.y = self.y
        result.z = self.x*math.sin(angle) + self.z*math.cos(angle)
        return result
    
    def rotateZ(self, angle):
        result = Vec3(0, 0, 0)
        result.x = self.x*math.cos(angle) + self.y*math.sin(angle)
        result.y = -self.x*math.sin(angle) + self.y*math.cos(angle)
        result.z = self.z
        return result
    
    def to_tuple(self):
        return (self.x, self.y, self.z, )
    
    def copy(self):
        return Vec3(self.x, self.y, self.z)



#--------------------------------------------------------------------
## parameters
#--------------------------------------------------------------------
terms = collections.defaultdict(lambda: Term(0))
length = 8
cy_radius = 0.9
collatz_lim = 4000 #4000 takes ≥ 15min, test below 1000

evenRotDiff = Vec3(rad(1), rad(2), rad(-6)) # more likely than odd
oddRotDiff = Vec3(rad(3), rad(-1), rad(6))



#--------------------------------------------------------------------
## functions
#--------------------------------------------------------------------
def main():
    """This is only fucnction called in file scope"""
    
    #delete all existing MESH
    delete_all()

    terms[1] = Term(1)

    #register numbers start from i
    for i in range(1, collatz_lim):
        sys.stdout.write("\rnow on : {}, {} terms generater".format(i, len(terms)))
        sys.stdout.flush()
        register_value(i)

    #make cylinders
    DFS()

    return


#----------------------------------
def register_value(n):
    """register n as element of collatz sequence to terms"""

    if terms[n].number != 0:
        return

    next_number = 0
    if n%2 == 0:
        next_number = n//2
    else:
        next_number = 3*n + 1

    register_value(next_number)

    terms[n] = Term(n)
    terms[next_number].prev_terms.append(n)

    return


#----------------------------------
def DFS():
    """visit every number in terms by depth first search"""

    start = terms[1]
    start.pos = Vec3(0, 0, 0)
    start.rot = Vec3(0, 0, 0)

    stack = collections.deque()
    stack.append(start)

    while stack:
        now = stack.pop()
        
        cylinder_asline(now.pos, now.rot)
        
        # make tree complex spiral-shape by rotating on every node.
        anglediff = Vec3(0, 0, 0)
        if now.number%2 == 0:
            anglediff = evenRotDiff
        else:
            anglediff = oddRotDiff

        for i, child in enumerate(now.prev_terms):
            
            new_pos = now.pos + Vec3.rotateXYZ(Vec3(0, 0, 1), now.rot).mult(length)

            new_rot = now.rot.copy()
            new_rot += anglediff.copy().mult(i+1)

            terms[child].pos = new_pos
            terms[child].rot = new_rot

            stack.append(terms[child])


#----------------------------------
def cylinder_asline(pos, rot):
    """make cylinder object based on one endpoint and heading vector"""
    center_pos = pos + Vec3.rotateXYZ(Vec3(0,0,1), rot).mult(length*0.5)
    bpy.ops.mesh.primitive_cylinder_add(location=center_pos.to_tuple(), radius=cy_radius, depth=length, rotation=(-rot).to_tuple()) #idk why negative is needed.


#----------------------------------
def delete_all():
    # Select objects by type
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            o.select_set(True)
        else:
            o.select_set(False)

    bpy.ops.object.delete()


main()
