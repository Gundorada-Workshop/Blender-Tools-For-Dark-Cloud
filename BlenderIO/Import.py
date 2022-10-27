import os
import math

import bpy
from bpy.props import CollectionProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Vector
import numpy as np

from ..DarkCloudModelTools.filetypes.CHR.CHRInterface import CHRInterface
from ..DarkCloudModelTools.filetypes.CHR.Model import Model
from ..DarkCloudModelTools.filetypes.IMG.ImageInterface import ImageInterface

UNIT_MATRIX =  Matrix([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

def vec_roll_to_mat3(vec, roll):
    """
    https://blender.stackexchange.com/a/38337
    """
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > 10**-10:
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix @ bMatrix
    return mat


def mat3_to_vec_roll(mat):
    """
    https://blender.stackexchange.com/a/38337
    """
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv @ mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    return vec, roll

class ImportDC(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_file.import_dark_cloud'
    bl_label = 'Dark Cloud (.chr)'
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.chr"

    files: CollectionProperty(type=bpy.types.PropertyGroup)

    # filter_glob: bpy.props.StringProperty(
    #                                          default="*.mlx",
    #                                          options={"HIDDEN"}
    #                                      )

    files: CollectionProperty(type=bpy.types.PropertyGroup)
    
    def execute(self, context):
        folder = (os.path.dirname(self.filepath))
        
        # add iteration through the selected files later
        self.import_file(context, self.filepath)

        return {'FINISHED'}
    
    def import_file(self, context, filepath):
        bpy.ops.object.select_all(action='DESELECT')
        
        ci = CHRInterface.from_file(filepath)
        model = Model.from_chr(ci)
        
        # Create Empty Axis
        filename = os.path.split(filepath)[-1]
        parent_obj = bpy.data.objects.new(filename, None)
        bpy.context.collection.objects.link(parent_obj)
        
        for submodel in model.submodels:
            # Create Armature
            armature_name = filename + "_armature"
            self.import_armature(parent_obj, armature_name, submodel)
            
            # Create Model
            textures = self.import_textures(submodel)
            self.import_meshes(bpy.data.objects[armature_name], submodel)
        
    def import_armature(self, parent_obj, armature_name, model):
        # DEFINITELY INCORRECT SOMEWHERE
        # Although many bones are placed at the "right" position, some
        # are placed at a noisy zero vector...
        
        # Create armature
        model_armature = bpy.data.objects.new(armature_name, bpy.data.armatures.new(armature_name))
        bpy.context.collection.objects.link(model_armature)
        model_armature.parent = parent_obj
    
        bpy.context.view_layer.objects.active = model_armature
        bpy.ops.object.mode_set(mode='EDIT')
        
        parents = {i : b.parent for i, b in enumerate(model.mds.bones)}
        matrices = [np.reshape(b.matrix, (4, 4)) for b in model.mds.bones]
        
        def combine_matrices(idx):
            if idx == -1:
                return np.eye(4)
            else:
                parent_idx = parents[idx]
                return matrices[idx] @ combine_matrices(parent_idx)
                
        
        list_of_bones = {}
        names = [b.name for b in model.mds.bones]
        total_matrices = [combine_matrices(i) for i in range(len(matrices))]
        for i, (bone_name, matrix) in enumerate(zip(names, total_matrices)):
            bone_name, _, _ = bone_name.partition(b'\x00')
            bone_name = bone_name.decode('ascii')
            
            bone = model_armature.data.edit_bones.new(bone_name)

            tail, roll = mat3_to_vec_roll(Matrix(matrix[:3, :3].tolist()))

            list_of_bones[i] = bone
            bone.head = Vector([0., 0., 0.])
            bone.tail = Vector([0., 1, 0.])  # Make this scale with the model size in the future, for convenience
            
            bone.head = Vector([*matrix[3, :3]])
            bone.tail = Vector([*matrix[3, :3]]) + tail
            bone.roll = roll

            parent = parents[i]
            if parent != -1:
                bone.parent = list_of_bones[parent]

                
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = parent_obj
        
    def generate_bone_idx_to_mesh_idx(self, model):
        bone_idx_to_mdt_idx = {}
        mdt_indices_lookup = model.mds.mdts.ptr_to_idx
        for i, bone in enumerate(model.mds.bones):
            if bone.mdt_offset in mdt_indices_lookup:#if bone.mdt_offset > 0:
                mdt_idx = mdt_indices_lookup[bone.mdt_offset]
                bone_idx_to_mdt_idx[bone.index] = mdt_idx
        return bone_idx_to_mdt_idx
        
    def generate_mesh_idx_to_bone_idx(self, model):
        return {m_idx : b_idx for b_idx, m_idx in self.generate_bone_idx_to_mesh_idx(model).items()}
    
    def generate_weights(self, model):
        bone_idx_to_mdt_idx = self.generate_bone_idx_to_mesh_idx(model)
        weights = {}
        for vertex_group in model.wgt.groups:
            mesh_idx = bone_idx_to_mdt_idx[vertex_group.meshbone_idx]
            if mesh_idx not in weights:
                weights[mesh_idx] = {}
            
            bone_idx = vertex_group.bone_idx
            if bone_idx not in weights[mesh_idx]:
                weights[mesh_idx][bone_idx] = []
            for e in vertex_group.elements:
                if e.weight > 0:
                    weights[mesh_idx][bone_idx].append((e.index, e.weight/100))
                
        return weights
        
    def import_textures(self, model):
        textures = []
        for img in model.imgs:
            for tm2_record, tm2 in zip(img.image_records, img.image_data):
                tm2_name = tm2_record.filename.partition(b'\x00')[0].decode('ascii')
                for i, tm2i in enumerate(tm2.images):
                    ii = ImageInterface.from_TM2(tm2i)
                    bpy_img = bpy.data.images.new(f"{tm2_name}_{i}", 
                                                  tm2i.header.image_width, 
                                                  tm2i.header.image_height)
                    bpy_img.pixels = [v for pixel in ii.pixels for v in pixel]
                    textures.append(bpy_img)
        return textures
    
    def import_meshes(self, armature, model):
        weights = self.generate_weights(model)
        mdt_idx_to_bone_idx = self.generate_mesh_idx_to_bone_idx(model)
        for i, mdt in enumerate(model.mds.mdts):
            verts   = [list(p[:3]) for p in mdt.positions]
            normals = [list(p[:3]) for p in mdt.normals]
            uvs     = [list(p[:2]) for p in mdt.UVs]
            tris = []
            for mesh in mdt.faces.strips:
                if mesh.type == 4:
                    for idx, (a, b, c) in enumerate(zip(mesh.indices, mesh.indices[1:], mesh.indices[2:])):
                        if idx % 2 == 0:
                            tris.append((a[0], b[0], c[0]))
                        else:
                            tris.append((b[0], a[0], c[0]))
                elif mesh.type == 3:
                    for idx, (a, b, c) in enumerate(zip(mesh.indices[::3], mesh.indices[1::3], mesh.indices[2::3])):
                        tris.append((a[0], b[0], c[0]))
                else:
                    raise NotImplementedError
            
            # Init mesh
            meshobj_name = f"mesh_{i}"
            bpy_mesh = bpy.data.meshes.new(name=meshobj_name)
            mesh_object = bpy.data.objects.new(meshobj_name, bpy_mesh)
            mesh_object.data.from_pydata(verts, [], tris)
            
            # Rig
            if i in weights:
                mesh_weights = weights[i]
                for bone_idx, mesh_bone_weights in mesh_weights.items():
                    vg_name = model.mds.bones[bone_idx].name.strip(b'\x00').decode('ascii')
                    vg = mesh_object.vertex_groups.new(name=vg_name)
                    for v_idx, v_weight in mesh_bone_weights:
                        vg.add([v_idx], v_weight, "REPLACE")
            elif i in mdt_idx_to_bone_idx:
                bone_idx = mdt_idx_to_bone_idx[i]
                vg_name = model.mds.bones[bone_idx].name.strip(b'\x00').decode('ascii')
                vg = mesh_object.vertex_groups.new(name=vg_name)
                for idx in range(len(verts)):
                    vg.add([idx], 1., "REPLACE")
                
            # Clean up
            mesh_object.parent = armature
            modifier = mesh_object.modifiers.new(name="Armature", type="ARMATURE")
            modifier.object = armature
            bpy.context.collection.objects.link(mesh_object)
                