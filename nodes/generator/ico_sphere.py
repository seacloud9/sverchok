
import bpy
import bmesh
from bpy.props import IntProperty, FloatProperty, BoolProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, match_long_repeat, SvSetSocketAnyType


def pydata_from_bmesh(bm):
    v = [v.co[:] for v in bm.verts]
    e = [[i.index for i in e.verts] for e in bm.edges[:]]
    p = [[i.index for i in p.verts] for p in bm.faces[:]]
    return v, e, p


def create_icospehere(subdiv, d):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, diameter=d)
    v, e, p = pydata_from_bmesh(bm)
    bm.free()
    return v, e, p


class IcoSphereNode(bpy.types.Node, SverchCustomTreeNode):
    ''' Sphere '''
    bl_idname = 'IcoSphereNode'
    bl_label = 'IcoSphere'

    Diameter = FloatProperty(
        name='Diameter', description='Ico Diameter',
        default=1.0,
        update=updateNode)

    Subdiv = IntProperty(
        name='Subdiv', description='Number of subdivs',
        default=3, min=3, max=6,
        update=updateNode)

    def sv_init(self, context):
        self.inputs.new('StringsSocket', "Diameter").prop_name = 'Diameter'
        self.inputs.new('StringsSocket', "Subdiv").prop_name = 'Subdiv'

        self.outputs.new('VerticesSocket', "Vertices")
        self.outputs.new('StringsSocket', "Edges")
        self.outputs.new('StringsSocket', "Polygons")

    def draw_buttons(self, context, layout):
        pass

    def process(self):
        Diameter = self.inputs['Diameter'].sv_get()[0]
        Subdivs = [max(int(sd), 3) for sd in self.inputs['Subdiv'].sv_get()[0]]

        params = match_long_repeat([Subdivs, Diameter])

        # outputs
        outputs = self.outputs
        if outputs['Vertices'].is_linked:

            multi_mesh = [create_icospehere(subdiv, d) for subdiv, d in zip(*params)]
            dlist = list(zip(*multi_mesh))
            verts = list(dlist[0])
            outputs['Vertices'].sv_set(verts)

            # doing this to avoid stdout messages.
            if outputs['Edges'].is_linked:
                edges = list(dlist[1])
                outputs['Edges'].sv_set(edges)

            if outputs['Polygons'].is_linked:
                faces = list(dlist[2])
                outputs['Polygons'].sv_set(faces)


def register():
    bpy.utils.register_class(IcoSphereNode)


def unregister():
    bpy.utils.unregister_class(IcoSphereNode)
