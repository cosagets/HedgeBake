# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "HedgeBake",
    "author" : "cosagets", 
    "description" : "A Blender addon that bakes GI maps for Hedgehog Engine 1 games using Cycles.",
    "blender" : (4, 5, 0),
    "version" : (1, 0, 1),
    "location" : "",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Render" 
}


import bpy
import bpy.utils.previews
import re
import sys
import os


addon_keymaps = {}
_icons = None
class SNA_PT_DIRECTORIES_D7D3B(bpy.types.Panel):
    bl_label = 'Directories'
    bl_idname = 'SNA_PT_DIRECTORIES_D7D3B'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'HedgeBake'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_4559D = layout.row(heading='', align=False)
        row_4559D.alert = False
        row_4559D.enabled = True
        row_4559D.active = True
        row_4559D.use_property_split = False
        row_4559D.use_property_decorate = False
        row_4559D.scale_x = 1.0
        row_4559D.scale_y = 1.0
        row_4559D.alignment = 'Expand'.upper()
        row_4559D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_4559D.label(text='Output Directory', icon_value=0)
        op = row_4559D.operator('file.external_operation', text='Open Directory', icon_value=0, emboss=True, depress=False)
        op.filepath = bpy.context.scene.sna_output_directory
        layout.prop(bpy.context.scene, 'sna_output_directory', text='', icon_value=0, emboss=True)
        row_DC03E = layout.row(heading='', align=False)
        row_DC03E.alert = False
        row_DC03E.enabled = True
        row_DC03E.active = True
        row_DC03E.use_property_split = False
        row_DC03E.use_property_decorate = False
        row_DC03E.scale_x = 1.0
        row_DC03E.scale_y = 1.0
        row_DC03E.alignment = 'Expand'.upper()
        row_DC03E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_DC03E.label(text='Render List', icon_value=0)
        op = row_DC03E.operator('sna.open_file_c5afb', text='Open File', icon_value=0, emboss=True, depress=False)
        layout.prop(bpy.context.scene, 'sna_render_list_file', text='', icon_value=0, emboss=True)


class SNA_PT_BAKE_OPTIONS_06FBA(bpy.types.Panel):
    bl_label = 'Bake Options'
    bl_idname = 'SNA_PT_BAKE_OPTIONS_06FBA'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'HedgeBake'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.label(text='Resolution', icon_value=0)
        layout.prop(bpy.context.scene, 'sna_resolution', text='', icon_value=196, emboss=True)
        row_ABFD7 = layout.row(heading='', align=False)
        row_ABFD7.alert = False
        row_ABFD7.enabled = True
        row_ABFD7.active = True
        row_ABFD7.use_property_split = False
        row_ABFD7.use_property_decorate = False
        row_ABFD7.scale_x = 1.0
        row_ABFD7.scale_y = 1.0
        row_ABFD7.alignment = 'Expand'.upper()
        row_ABFD7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_ABFD7.prop(bpy.context.scene, 'sna_use_render_list', text='Use Render List', icon_value=0, emboss=True)
        row_ABFD7.prop(bpy.context.scene, 'sna_denoise', text='Denoise', icon_value=0, emboss=True)
        row_CC62E = layout.row(heading='', align=False)
        row_CC62E.alert = False
        row_CC62E.enabled = True
        row_CC62E.active = True
        row_CC62E.use_property_split = False
        row_CC62E.use_property_decorate = False
        row_CC62E.scale_x = 1.0
        row_CC62E.scale_y = 1.0
        row_CC62E.alignment = 'Expand'.upper()
        row_CC62E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_CC62E.prop(bpy.context.scene, 'sna_skip_existing_files', text='Skip Existing Files', icon_value=0, emboss=True)


class SNA_PT_BAKE_C73FF(bpy.types.Panel):
    bl_label = 'Bake'
    bl_idname = 'SNA_PT_BAKE_C73FF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'HedgeBake'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        op = layout.operator('sna.bake_44e3c', text='Bake', icon_value=190, emboss=True, depress=False)


class SNA_OT_Bake_44E3C(bpy.types.Operator):
    bl_idname = "sna.bake_44e3c"
    bl_label = "Bake"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        path = bpy.context.scene.sna_output_directory
        render_list = bpy.context.scene.sna_render_list_file
        use_render_list = bpy.context.scene.sna_use_render_list
        use_denoise = bpy.context.scene.sna_denoise
        bake_resolution = bpy.context.scene.sna_resolution
        skip_existing_files = bpy.context.scene.sna_skip_existing_files
        no_issues = None
        import os
        import time
        # Start timer
        start_time = time.perf_counter()
        os.system('cls')
        selected_objects = bpy.context.selected_objects
        sunlight = bpy.data.objects.get("Sun")
        issues_found = []
        no_issues = False
        # Checks for errors when trying to save to the path

        def check_path():
            try:
                test_image = bpy.data.images.new("test_image", 128, 128)
                test_image.filepath_raw = path + "test_image.png"
                test_image.save()
                bpy.data.images.remove(bpy.data.images["test_image"])
                os.remove(path + "test_image.png")
            except Exception as e:
                bpy.data.images.remove(bpy.data.images["test_image"])
                issues_found.append("The current output directory isn't writable.")
        # Check if scene is using cycles

        def check_for_cycles():
            if bpy.context.scene.render.engine != 'CYCLES':
                issues_found.append("Cycles needs to be enabled.")
        # Checks if 'Use Nodes' is enabled in compositor

        def check_for_compositor_nodes():
            if bpy.context.scene.use_nodes == True:
                pass
            else:
                issues_found.append("Enable the 'Use Nodes' option in the compositor")
        # Check what the current frame is

        def check_current_frame():
            if bpy.context.scene.frame_current != 1:
                issues_found.append(f"Current frame number needs to be set to 1. It is currently {bpy.context.scene.frame_current}")
        # Check if there's a sun light in the scene

        def check_for_sunlight():
            sun_exists = False
            for obj in bpy.context.scene.objects:
                if obj.type == 'LIGHT' and obj.data.type == 'SUN':
                    sun_exists = True
                    break
            if sun_exists:
                pass
            else:
                issues_found.append("No Sun light found in the scene.")
        # Check if the sunlight has a light linking collection

        def check_light_linking():
            for obj in bpy.context.scene.objects:
                if obj.type == 'LIGHT' and obj.data.type == 'SUN':
                    if sunlight.light_linking.receiver_collection:
                        pass
                    else:
                        issues_found.append("A light linking collection needs to be selected for the Sun light.")
                        issues_found.append("    -Select your sun and go to its Object properties.")
                        issues_found.append("    -Under Shading and Light Linking, select the collection containing "
                        "all the objects that will have GI rendered for it.")
        # Check if there's a background node in the World node tree

        def check_for_background_node():
            world = bpy.context.scene.world
            if world and world.use_nodes and world.node_tree:
                node_tree = world.node_tree
                background_node = node_tree.nodes.get("Background")
                if background_node:
                    pass
                else:
                    issues_found.append("The 'Background' node does not exist in the World's node tree.")
            else:
                issues_found.append("The World isn't using nodes.")
                issues_found.append("    -Go to the shader editor and check 'Use Nodes' in the World shader type.")
                issues_found.append("    -Make sure the Background node is connected to the World Output node.")
        # Check if there's a camera in the scene

        def check_for_camera_in_scene():
            camera_exists = False
            for obj in bpy.context.scene.objects:
                if obj.type == 'CAMERA':
                    camera_exists = True
                    break
            if camera_exists:
                pass
            else:
                issues_found.append("No camera found in the scene. (Needed for denoising)")
        # Check if object is selected

        def check_for_selected_objects():
            if bpy.context.selected_objects:
                return True
            else:
                issues_found.append("No objects are selected.")
        # Check if there's an active MESH object

        def check_active_object():
            if bpy.context.active_object:
                if bpy.context.active_object.type != 'MESH':
                    issues_found.append("Current active object is not a mesh object")
            else:
                issues_found.append("There is no active object")
                return None
        # Checks if active object is currently in object mode

        def check_for_object_mode():
            current_mode = bpy.context.object.mode
            if current_mode == 'OBJECT':
                pass
            else:
                issues_found.append("Need to be in Object mode.")
        # Check if object has second uv channel

        def check_for_second_uv_channel(obj):
            if len(obj.data.uv_layers) >= 2:
                pass
            else:
                issues_found.append(f"{obj.name} does not have second uv channel.")
        # Check if object has materials

        def check_for_materials(obj):
            if len(obj.material_slots) == 0:
                issues_found.append(f"{obj.name} has no materials.")
            elif obj.active_material is None:
                issues_found.append(f"{obj.name} has an empty material.")
        # Checks if object is renderable

        def check_for_renderable(obj):
            if obj.hide_render:
                issues_found.append(f"{obj.name} needs to be made renderable.")
        # Checks for duplicate object names that will occue after renaming them

        def check_for_duplicates(obj):
            original_name = obj.name
            new_name = obj.name
            # Sets new name to be the old name with periods replaced by underscores
            if '.' in original_name or '@' in original_name:
                new_name = original_name.replace('.', '_')
                # If the @ symbol is found, removes everything after it
                if '@' in new_name:
                    name_parts = new_name.split('@', 1)
                    new_name = name_parts[0]
                # Checks if the new name already exists in the scene
                while new_name in bpy.data.objects != obj:
                    issues_found.append(
                    f"{obj.name} must be renamed to avoid having a duplicate"
                    f" name with another object named {new_name}"
                    )
                    break
        # Performs the same function as in the main script but will catch errors

        def check_renderlist(obj):
            data_rows = []
            try:
                with open(render_list, 'r') as f:
                    for line in f:
                        columns = line.strip().split(' ')
                        data_rows.append(columns)
            except FileNotFoundError:
                issues_found.append("File not found at the Render List destination")
            try:
                for i in range(len(data_rows)):
                    if data_rows[i][1] == obj.name:
                        bake_resolution = data_rows[i][0]
                        return bake_resolution
            except Exception as e:
                issues_found.append(f"There was an issue reading the render list: {e}")
        # Displays message showing current issues preventing baking

        def ShowMessageBox(title = "Issues Found", icon = 'ERROR', message=""):
            issues_found=message

            def draw(self, context):
                for n in range(len(issues_found)):
                    self.layout.label(text=issues_found[n])
            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        check_path()
        check_for_cycles()
        check_for_compositor_nodes()
        check_current_frame()
        check_for_sunlight()
        check_light_linking()
        check_for_background_node()
        if use_denoise == True:
            check_for_camera_in_scene()
        if check_for_selected_objects() == True:
            if check_active_object() != None:
                check_for_object_mode()
        for obj in selected_objects:
            if obj.type == 'MESH':
                check_for_second_uv_channel(obj)
                check_for_materials(obj)
                check_for_renderable(obj)
                check_for_duplicates(obj)
                if use_render_list == True:
                    check_renderlist(obj)
            else:
                issues_found.append("Select only mesh objects. No lights, curves, cameras, etc.")
                break
        if len(issues_found) == 0:
            no_issues = True
        else:
            ShowMessageBox(message=issues_found)
        if no_issues:
            background_node = bpy.data.worlds["World"].node_tree.nodes["Background"]
            background_color = bpy.context.scene.world.color
            compositor = bpy.context.scene.node_tree
            sunlight = bpy.data.lights["Sun"]
            temp_path = bpy.app.tempdir
            original_settings = {
                "bake_margin": bpy.context.scene.render.bake.margin,
                "bake_margin_type": bpy.context.scene.render.bake.margin_type,
                "view_transform": bpy.context.scene.view_settings.view_transform,
                "resolution_percentage": bpy.context.scene.render.resolution_percentage,
                "sunlightR": sunlight.color.r,
                "sunlightG": sunlight.color.g,
                "sunlightB": sunlight.color.b,
                "sun_strength": sunlight.energy,
                "sun_exposure": sunlight.exposure,
                "background_strength": background_node.inputs["Strength"].default_value,
                "background_colorR": background_color.r,
                "background_colorG": background_color.g,
                "background_colorB": background_color.b,
                "light_bounces": bpy.context.scene.cycles.max_bounces,
            }
            original_visibility = {}
            original_metallic = {}
            original_emission = {}
            original_names = {}

            def timer(seconds):
                min, sec = divmod(seconds, 60)
                hour, min = divmod(min, 60)
                return '%dh:%02dm:%02ds' % (hour, min, sec)

            def update_progress(job_title, progress):
                length = 20 # modify this to change the length
                block = int(round(length*progress))
                msg = "\r{0}: [{1}] {2}%\n\n".format(job_title, "#"*block + "-"*(length-block), round((progress*100), 2))
                if progress >= 1 and job_title == "Baking shadowmaps": msg += "DONE\n"
                sys.stdout.write(msg)
                sys.stdout.flush()
            # Create a bakemap image node in every material at the specified resolution
            # Disables all normals and sets metallic values to 0

            def create_bakemap(bake_resolution):
                # noprint("Creating bakemap and bakemap image nodes...")
                bakemap = bpy.data.images.new("bakemap", int(bake_resolution), int(bake_resolution))
                for material in bpy.data.materials:
                    if material.name == "Dots Stroke":
                        continue
                    material.use_nodes = True
                    bakemap_image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
                    material.node_tree.nodes.active = bakemap_image_node
                    bakemap_image_node.image = bakemap
                    # Disables all normals and metallic values
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            original_metallic[node] = node.inputs['Metallic'].default_value
                            node.inputs['Metallic'].default_value = 0
                        if node.type == 'NORMAL_MAP':
                            node.inputs['Strength'].default_value = 0
            # Set up and store compositor and render settings for denoising

            def change_other_settings():
                # noprint("Changing other settings...")
                bpy.context.scene.view_settings.view_transform = 'Standard'
                bpy.context.scene.render.resolution_percentage = 1
                bpy.context.scene.render.bake.margin = 512
                bpy.context.scene.render.bake.margin_type = 'EXTEND'
            # Creates temporary collection

            def create_temporary_collection():
                # noprint("Creating temporary collection...\n")
                global temporary_collection
                temporary_collection = bpy.data.collections.new(name="TempCollection")
                bpy.context.scene.collection.children.link(temporary_collection)
            # Selects the second UV Channel of the selected objects

            def select_second_uv_channel(obj):
                # noprint("Selecting second uv channel...")
                obj.data.uv_layers.active_index = 1
            # Renames objects to match name changes that happen when using Hedgehog Converter

            def rename_objects(obj):
                original_name = obj.name
                new_name = obj.name
                # Sets new name to be the old name with periods replaced by underscores
                if '.' in original_name or '@' in original_name:
                    new_name = original_name.replace('.', '_')
                    # If the @ symbol is found, removes everything after it
                    if '@' in new_name:
                        name_parts = new_name.split('@', 1)
                        new_name = name_parts[0]
                    original_names[new_name] = obj.name # Stores original name with new name as key
                    # noprint(f"Renaming {original_name} to {new_name}")
                    obj.name = new_name
            # Moves object into temporary collection
            # With light linking, this will remove the direct sun light from bakes
            # while maintaining its indirect light contributions

            def move_to_temporary_collection(obj):
                # noprint("Moving to temporary collection...")
                temporary_collection.objects.link(obj)
                currentCollection[0].objects.unlink(obj)
            # Bakes lightmaps using direct and indirect bake type and saves them

            def bake_lightmaps(obj, bakemap, savefile):
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bakemap.file_format = 'PNG'
                # noprint("Baking lightmaps...")
                bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT','INDIRECT'})
                if savefile == True:
                    bakemap.filepath_raw = path + obj.name + "_lightmap.png"
                    bakemap.save()
            # Moves object back to its original collection

            def move_to_original_collection(obj):
                # noprint("Moving to back to original collection...")
                currentCollection[0].objects.link(obj)
                temporary_collection.objects.unlink(obj)
            # Takes the square root of the image's RGB values and saves the image
            # Hedgehog Engine games multiply GI maps with themselves when in-game, making them darker
            # Saving the square root of the image's RGB values counteracts the darkening

            def sqrt_and_save(obj, current_map):
                # noprint("Processing images and saving...")
                image_node = compositor.nodes.new(type='CompositorNodeImage')
                image_node.image = bpy.data.images.get("bakemap")
                file_output_node = compositor.nodes.new('CompositorNodeOutputFile')
                file_output_node.base_path = path
                file_output_node.file_slots[0].path = obj.name + current_map
                separate_color_node = compositor.nodes.new(type='CompositorNodeSeparateColor')
                math_nodeR = compositor.nodes.new(type='ShaderNodeMath')
                math_nodeR.operation = 'SQRT'
                math_nodeG = compositor.nodes.new(type='ShaderNodeMath')
                math_nodeG.operation = 'SQRT'
                math_nodeB = compositor.nodes.new(type='ShaderNodeMath')
                math_nodeB.operation = 'SQRT'
                combine_color_node = compositor.nodes.new(type='CompositorNodeCombineColor')
                compositor.links.new(image_node.outputs["Image"], separate_color_node.inputs["Image"])
                compositor.links.new(separate_color_node.outputs["Red"], math_nodeR.inputs["Value"])
                compositor.links.new(separate_color_node.outputs["Green"], math_nodeG.inputs["Value"])
                compositor.links.new(separate_color_node.outputs["Blue"], math_nodeB.inputs["Value"])
                compositor.links.new(math_nodeR.outputs["Value"], combine_color_node.inputs["Red"])
                compositor.links.new(math_nodeG.outputs["Value"], combine_color_node.inputs["Green"])
                compositor.links.new(math_nodeB.outputs["Value"], combine_color_node.inputs["Blue"])
                compositor.links.new(combine_color_node.outputs["Image"], file_output_node.inputs["Image"])
                bpy.ops.render.render(write_still=True)
            # Removes the .png0001 suffix placed on output files by default

            def rename_saved_files(obj, current_map):
                # Sets the current frame to 1 so the .png0001 suffix can be placed by Blender and replaced by the script
                bpy.context.scene.frame_current = 1
                old_filepath = os.path.join(path + obj.name + current_map + ".png0001.png")
                filename = os.path.join(obj.name + current_map + ".png0001.png")
                if os.path.isfile(old_filepath): # Checks if it's a file and not a subdirectory
                    new_filename = filename.replace(".png0001", "")
                    new_filepath = os.path.join(path, new_filename)
                    try:
                        os.rename(old_filepath, new_filepath)
                    except FileExistsError:
                        # noprint(f"{new_filename} already exists. Deleting...")
                        os.remove(new_filepath)
                        os.rename(old_filepath, new_filepath)
                        # noprint(f"Renamed '{filename}' to '{new_filename}'")
            # Remove compositor nodes created by the script

            def remove_compositor_nodes():
                # noprint("Removing compositor nodes...")
                for node in compositor.nodes:
                    if node.type != 'R_LAYERS' and node.type != 'COMPOSITE' and node.type != 'REROUTE' and node.type != 'VIEWER':
                        compositor.nodes.remove(node)
            # Restores object names

            def restore_names(obj):
                if obj.name in original_names:
                    # noprint(f"Renaming {obj.name} back to {original_names[obj.name]}")
                    obj.name = original_names[obj.name]
            # Selects the first uv channel

            def select_first_uv_channel(obj):
                # noprint("Selecting first UV Channel...\n")
                obj.data.uv_layers.active_index = 0
            # Gets a bake resolution from the render list file if available
            # If not, will use the default bake resolution

            def get_renderlist_resolution(obj, default_resolution):
                data_rows = []
                with open(render_list, 'r') as f:
                    for line in f:
                        columns = line.strip().split(' ')
                        data_rows.append(columns)
                # Checks if the object name is found in the render list then sets the
                # number next to it as the bake resolution
                for i in range(len(data_rows)):
                    if data_rows[i][1] == obj.name:
                        bake_resolution = data_rows[i][0]
                        # noprint(f"Bake resolution for {obj.name} is {bake_resolution}")
                        return int(bake_resolution)
                # noprint(f"{obj.name} not found in render list. Using default resolution of {default_resolution}")
                return int(default_resolution)
            # Sets up the compositor nodes for denoising and saving the
            # square root of the image's RGB values

            def sqrt_denoise_and_save(obj, current_map):
                # noprint("Processing images and saving...")
                image_node = compositor.nodes.new(type='CompositorNodeImage')
                image_node.image = bpy.data.images.get("bakemap")
                file_output_node = compositor.nodes.new('CompositorNodeOutputFile')
                file_output_node.base_path = path
                file_output_node.file_slots[0].path = obj.name + current_map
                denoise_node = compositor.nodes.new(type='CompositorNodeDenoise')
                denoise_node.use_hdr = False
                if current_map == "_shadowmap.png":
                    compositor.links.new(image_node.outputs["Image"], denoise_node.inputs["Image"])
                    compositor.links.new(denoise_node.outputs["Image"], file_output_node.inputs["Image"])
                    bpy.ops.render.render(write_still=True)
                    return
                separate_color_node = compositor.nodes.new(type='CompositorNodeSeparateColor')
                math_nodeR = compositor.nodes.new(type='ShaderNodeMath')
                math_nodeR.operation = 'SQRT'
                math_nodeG = compositor.nodes.new(type='ShaderNodeMath')
                math_nodeG.operation = 'SQRT'
                math_nodeB = compositor.nodes.new(type='ShaderNodeMath')
                math_nodeB.operation = 'SQRT'
                combine_color_node = compositor.nodes.new(type='CompositorNodeCombineColor')
                compositor.links.new(image_node.outputs["Image"], separate_color_node.inputs["Image"])
                compositor.links.new(separate_color_node.outputs["Red"], math_nodeR.inputs["Value"])
                compositor.links.new(separate_color_node.outputs["Green"], math_nodeG.inputs["Value"])
                compositor.links.new(separate_color_node.outputs["Blue"], math_nodeB.inputs["Value"])
                compositor.links.new(math_nodeR.outputs["Value"], combine_color_node.inputs["Red"])
                compositor.links.new(math_nodeG.outputs["Value"], combine_color_node.inputs["Green"])
                compositor.links.new(math_nodeB.outputs["Value"], combine_color_node.inputs["Blue"])
                compositor.links.new(combine_color_node.outputs["Image"], denoise_node.inputs["Image"])
                compositor.links.new(denoise_node.outputs["Image"], file_output_node.inputs["Image"])
                bpy.ops.render.render(write_still=True)
            # Removes temporary collection.

            def remove_temporary_collection():
                # noprint("Removing temporary collection...\n")
                bpy.data.collections.remove(temporary_collection)
            # Set Sun strength to 12, and background strength, emission strength, and total scene light bounces to 0

            def change_light_setup():
                # noprint("Changing light setup...\n")
                sunlight.color = 1.0, 1.0, 1.0
                sunlight.energy = 5
                sunlight.exposure = 0
                background_node.inputs["Strength"].default_value = 0
                background_color = (0, 0, 0)
                bpy.context.scene.cycles.max_bounces = 0
                for obj in bpy.context.scene.objects:
                    if obj.type == 'LIGHT':
                        if obj.data.type == 'SUN':
                            obj.hide_render = False
                        else:
                            original_visibility[obj.name] = obj.hide_render # Stores the current visibility of the light
                            obj.hide_render = True
                # Sets all emission values to 0
                for material in bpy.data.materials:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            original_emission[node] = node.inputs['Emission Strength'].default_value
                            node.inputs['Emission Strength'].default_value = 0
            # Bakes shadowmaps using direct bake type and saves them

            def bake_shadowmaps(obj, bakemap, savefile):
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bakemap.file_format = 'PNG'
                # noprint("Baking shadowmaps...")
                bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT'})
                if savefile == True:
                    bakemap.filepath_raw = path + obj.name + "_shadowmap.png"
                    bakemap.save()
            # Restores original light setup

            def restore_light_setup():
                # noprint("Restoring light setup...")
                # Set sun strength, background strength, and total light bounces back to their previous values
                sunlight.color.r = original_settings["sunlightR"]
                sunlight.color.g = original_settings["sunlightG"]
                sunlight.color.b = original_settings["sunlightB"]
                sunlight.energy = original_settings["sun_strength"]
                sunlight.exposure = original_settings["sun_exposure"]
                background_node.inputs["Strength"].default_value = original_settings["background_strength"]
                background_color.r = original_settings["background_colorR"]
                background_color.g = original_settings["background_colorG"]
                background_color.b = original_settings["background_colorB"]
                bpy.context.scene.cycles.max_bounces = original_settings["light_bounces"]
                # Enable all lights that were disabled by the script
                for obj, visibility_state in original_visibility.items():
                    bpy.context.scene.objects[obj].hide_render = visibility_state
                # Restores emission values
                for material in bpy.data.materials:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.inputs['Emission Strength'].default_value = original_emission[node]
            # Restore compositor and render settings

            def restore_other_settings():
                # noprint("Restoring compositor settings...")
                bpy.context.scene.view_settings.view_transform = original_settings["view_transform"]
                bpy.context.scene.render.resolution_percentage = original_settings["resolution_percentage"]
                bpy.context.scene.render.bake.margin = original_settings["bake_margin"]
                bpy.context.scene.render.bake.margin_type = original_settings["bake_margin_type"]
            # Removes bakemap texture, its image node, and re-enables all normals

            def remove_bakemap():
                # noprint("Removing bakemap and bakemap image nodes")
                bpy.data.images.remove(bpy.data.images["bakemap"])
                for material in bpy.data.materials:
                    if material.name == "Dots Stroke":
                        continue
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.inputs['Metallic'].default_value = original_metallic[node]
                        if node.type == 'NORMAL_MAP':
                            node.inputs['Strength'].default_value = 1
                        if node == material.node_tree.nodes.active:
                            material.node_tree.nodes.remove(node)
            create_bakemap(bake_resolution)
            change_other_settings()
            create_temporary_collection()
            for obj in selected_objects:
                os.system('cls')
                update_progress("Baking lightmaps", selected_objects.index(obj)/len(selected_objects))
                update_progress("Baking shadowmaps", 0)
                print(f"Processing... {obj.name} ", end='')
                currentCollection = obj.users_collection # Gets the current collection of the object
                select_second_uv_channel(obj)
                rename_objects(obj)
                if skip_existing_files == True:
                    if os.path.exists(path + obj.name + "_lightmap.png"):
                        # noprint(f"Lightmap texture already exists. Skipping...")
                        restore_names(obj)
                        select_first_uv_channel(obj)
                        continue
                if use_render_list == True:
                    bake_resolution = get_renderlist_resolution(obj, bake_resolution)
                print(f"({bake_resolution}x{bake_resolution})")
                bpy.data.images.get("bakemap").scale(int(bake_resolution), int(bake_resolution))
                move_to_temporary_collection(obj)
                if use_denoise == True:
                    bake_lightmaps(obj, bpy.data.images["bakemap"], False)
                    move_to_original_collection(obj)
                    sqrt_denoise_and_save(obj, "_lightmap.png")
                    rename_saved_files(obj, "_lightmap")
                    remove_compositor_nodes()
                    restore_names(obj)
                    select_first_uv_channel(obj)
                    continue
                bake_lightmaps(obj, bpy.data.images["bakemap"], False)
                move_to_original_collection(obj)
                sqrt_and_save(obj, "_lightmap.png")
                rename_saved_files(obj, "_lightmap")
                remove_compositor_nodes()
                restore_names(obj)
                select_first_uv_channel(obj)
            remove_temporary_collection()
            change_light_setup()
            for obj in selected_objects:
                os.system('cls')
                update_progress("Baking lightmaps", 1)
                update_progress("Baking shadowmaps", selected_objects.index(obj)/len(selected_objects))
                print(f"Processing... {obj.name} ", end='')
                select_second_uv_channel(obj)
                rename_objects(obj)
                if skip_existing_files == True:
                    if os.path.exists(path + obj.name + "_shadowmap.png"):
                        # noprint(f"Shadowmap texture already exists. Skipping...")
                        restore_names(obj)
                        select_first_uv_channel(obj)
                        continue
                if use_render_list == True:
                    bake_resolution = get_renderlist_resolution(obj, bake_resolution)
                print(f"({bake_resolution}x{bake_resolution})")
                bpy.data.images.get("bakemap").scale(int(bake_resolution), int(bake_resolution))
                if use_denoise == True:
                    bake_shadowmaps(obj, bpy.data.images["bakemap"], False)
                    sqrt_denoise_and_save(obj, "_shadowmap.png")
                    rename_saved_files(obj, "_shadowmap")
                    remove_compositor_nodes()
                    restore_names(obj)
                    select_first_uv_channel(obj)
                    continue
                bake_shadowmaps(obj, bpy.data.images["bakemap"], True)
                restore_names(obj)
                select_first_uv_channel(obj)
            os.system('cls')
            update_progress("Baking lightmaps", 1)
            update_progress("Baking shadowmaps", 1)
            restore_light_setup()
            restore_other_settings()
            remove_bakemap()
            for obj in selected_objects:
                obj.select_set(True)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"\nFinished in {timer(elapsed_time)}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Open_File_C5Afb(bpy.types.Operator):
    bl_idname = "sna.open_file_c5afb"
    bl_label = "Open File"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        path = bpy.context.scene.sna_render_list_file

        def ShowMessageBox(title = "Error", icon = 'ERROR', message=""):

            def draw(self, context):
                self.layout.label(text=message)
            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        try:
            os.startfile(path)
        except Exception as e:
            ShowMessageBox(message = "Could not find file")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.sna_resolution = bpy.props.EnumProperty(name='Resolution', description='', items=[('16', '16', '', 0, 0), ('32', '32', '', 0, 1), ('64', '64', '', 0, 2), ('128', '128', '', 0, 3), ('256', '256', '', 0, 4), ('512', '512', '', 0, 5), ('1024', '1024', '', 0, 6), ('2048', '2048', '', 0, 7)])
    bpy.types.Scene.sna_use_render_list = bpy.props.BoolProperty(name='Use Render List', description='', default=True)
    bpy.types.Scene.sna_denoise = bpy.props.BoolProperty(name='Denoise', description='', default=True)
    bpy.types.Scene.sna_output_directory = bpy.props.StringProperty(name='Output Directory', description='', default='', subtype='DIR_PATH', maxlen=0)
    bpy.types.Scene.sna_denoised_directory = bpy.props.StringProperty(name='Denoised Directory', description='', default='', subtype='DIR_PATH', maxlen=0)
    bpy.types.Scene.sna_render_list_file = bpy.props.StringProperty(name='Render List File', description='', default='', subtype='FILE_PATH', maxlen=0)
    bpy.types.Scene.sna_skip_existing_files = bpy.props.BoolProperty(name='Skip Existing Files', description='', default=True)
    bpy.utils.register_class(SNA_PT_DIRECTORIES_D7D3B)
    bpy.utils.register_class(SNA_PT_BAKE_OPTIONS_06FBA)
    bpy.utils.register_class(SNA_PT_BAKE_C73FF)
    bpy.utils.register_class(SNA_OT_Bake_44E3C)
    bpy.utils.register_class(SNA_OT_Open_File_C5Afb)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_skip_existing_files
    del bpy.types.Scene.sna_render_list_file
    del bpy.types.Scene.sna_denoised_directory
    del bpy.types.Scene.sna_output_directory
    del bpy.types.Scene.sna_denoise
    del bpy.types.Scene.sna_use_render_list
    del bpy.types.Scene.sna_resolution
    bpy.utils.unregister_class(SNA_PT_DIRECTORIES_D7D3B)
    bpy.utils.unregister_class(SNA_PT_BAKE_OPTIONS_06FBA)
    bpy.utils.unregister_class(SNA_PT_BAKE_C73FF)
    bpy.utils.unregister_class(SNA_OT_Bake_44E3C)
    bpy.utils.unregister_class(SNA_OT_Open_File_C5Afb)
