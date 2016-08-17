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
        ...

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
