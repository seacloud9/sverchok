# BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# END GPL LICENSE BLOCK #####

import itertools

import bpy
from bpy.types import Operator


class SvNodeHotSwap(bpy.types.Operator):

    bl_idname = "node.sv_nodeswap_intfloat"
    bl_label = "Short Name"
    # bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        node = context.active_node

        if not node:
            return

        return any([(s in node.bl_idname) for s in ["Float", "Int"]])

    def hot_replace(self, node, replace_with):
        node_tree = node.id_data
        props_to_copy = 'bl_idname name location height width'.split(' ')

        def flatten(L):
            return L.from_node.name, L.from_socket.index, L.to_node.name, L.to_socket.index

        reconnections = {'inputs': [], 'outputs': []}
        for sockets in reconnections.keys():
            for s in (s for s in getattr(node, sockets) if s.is_linked):
                for L in s.links:
                    reconnections[sockets].append(flatten(L))

        props = {j: getattr(node, j) for j in props_to_copy}

        new_node = node_tree.nodes.new(replace_with)
        props_to_copy.pop(0)

        for prop in props_to_copy:
            setattr(new_node, prop, props[prop])

        if 'Range' in node.bl_idname:
            ops = ['LAZYRANGE', 'COUNTRANGE', 'LAZYRANGE', 'FRANGE', 'FRANGE_COUNT', 'FRANGE_STEP']

            idx = ops.index(node.mode)
            rfx = idx-3 if idx > 2 else idx+3
            new_node.mode = ops[rfx]
            
        nodes = node_tree.nodes
        nodes.remove(node)
        new_node.name

        # outputs [('List Range Int.002', 0, 'List Range Int.003', 0), ('List Range Int.002', 0, 'List Range Int.003', 1)]
        # inputs [('Integer', 0, 'List Range Int.002', 0), ('Integer', 0, 'List Range Int.002', 2)]

        for k, v in reconnections.items():
            print(k, v)
            for j in v:
                if k == 'inputs':
                    a, b = nodes[j[0]].outputs[j[1]], new_node.inputs[j[3]]
                else:
                    a, b = new_node.outputs[j[1]], nodes[j[2]].inputs[j[3]]
                node_tree.links.new(a, b)


    def execute(self, context):
        float_range = "SvGenFloatRange"
        int_range = "GenListRangeIntNode"
        float_single = "FloatNode"
        int_single = "IntegerNode"

        node = context.active_node
        idname = node.bl_idname

        replace_with = {
            float_range: int_range, 
            int_range: float_range,
            float_single: int_single,
            int_single: float_single
        }.get(idname)

        if replace_with:
            self.hot_replace(node, replace_with)

        return {'FINISHED'}


classes = [SvNodeHotSwap]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
