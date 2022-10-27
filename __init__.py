import bpy
from .BlenderIO.Import import ImportDC


bl_info = {
        "name": "Dark Cloud Import/Export (.name)",
        "description": "Imports model and animation files from Dark Cloud.",
        "author": "Pherakki",
        "version": (0, 1),
        "blender": (2, 80, 0),
        "location": "File > Import, File > Export",
        "warning": "",
        "category": "Import-Export",
        }


class DCImportSubmenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_DarkCloud_import_submenu"
    bl_label = "Dark Cloud"

    def draw(self, context):
        layout = self.layout
        layout.operator(ImportDC.bl_idname, text="Dark Cloud Model (.chr)")


def menu_func_import(self, context):
    self.layout.menu(DCImportSubmenu.bl_idname)


def register():
    blender_version = bpy.app.version_string  # Can use this string to switch version-dependent Blender API codes
    bpy.utils.register_class(ImportDC)
    bpy.utils.register_class(DCImportSubmenu)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportDC)
    bpy.utils.unregister_class(DCImportSubmenu)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

# if __name__ == "__main__":
#     register()
