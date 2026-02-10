import bpy
import os
import re
import time
import sys

os.system('cls')

# Start timer
start_time = time.perf_counter()

selected_objects = bpy.context.selected_objects
path = "C:/Users/Colin/Desktop/Sega/Modding/Projects/Render Test/GITextures/"
render_list = "C:/Users/Colin/Desktop/Sega/Modding/Projects/Render Test/RenderList.txt"
use_render_list = True
use_denoise = True
bake_resolution = 1024
skip_existing_files = False
background_node = bpy.data.worlds["World"].node_tree.nodes["Background"]
background_color = bpy.context.scene.world.color
compositor = bpy.context.scene.compositing_node_group
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
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.render.resolution_percentage = 1
    bpy.context.scene.render.bake.margin = 512
    bpy.context.scene.render.bake.margin_type = 'EXTEND'
    
# Creates temporary collection
def create_temporary_collection():
    global temporary_collection
    temporary_collection = bpy.data.collections.new(name="TempCollection")
    bpy.context.scene.collection.children.link(temporary_collection)

# Selects the second UV Channel of the selected objects
def select_second_uv_channel(obj):
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
        obj.name = new_name

# Moves object into temporary collection
# With light linking, this will remove the direct sun light from bakes
# while maintaining its indirect light contributions
def move_to_temporary_collection(obj):
    temporary_collection.objects.link(obj)
    currentCollection[0].objects.unlink(obj)

# Bakes lightmaps using direct and indirect bake type and saves them
def bake_lightmaps(obj, bakemap, savefile):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bakemap.file_format = 'PNG'
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT','INDIRECT'})
    if savefile == True:
        bakemap.filepath_raw = path + obj.name + "_lightmap.png"
        bakemap.save()
    
# Moves object back to its original collection
def move_to_original_collection(obj):
    currentCollection[0].objects.link(obj)
    temporary_collection.objects.unlink(obj)

# Takes the square root of the image's RGB values and saves the image
# Hedgehog Engine games multiply GI maps with themselves when in-game, making them darker
# Saving the square root of the image's RGB values counteracts the darkening
def sqrt_and_save(obj, current_map):
    image_node = compositor.nodes.new(type='CompositorNodeImage')
    image_node.image = bpy.data.images.get("bakemap")
    file_output_node = compositor.nodes.new('CompositorNodeOutputFile')
    file_output_node.directory = path
    file_output_node.format.media_type = 'IMAGE'
    file_output_node.file_output_items.new(socket_type='RGBA', name="Image")
    file_output_node.file_name = obj.name + current_map
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
    
# Removes the .pngImage suffix placed on output files by default
def rename_saved_files(obj, current_map):
    # Sets the current frame to 1 so the .pngImage suffix can be placed by Blender and replaced by the script
    bpy.context.scene.frame_current = 1
    
    old_filepath = os.path.join(path + obj.name + current_map + ".pngImage.png")
    filename = os.path.join(obj.name + current_map + ".pngImage.png")
    
    if os.path.isfile(old_filepath): # Checks if it's a file and not a subdirectory
        new_filename = filename.replace(".pngImage", "")
        new_filepath = os.path.join(path, new_filename)
        try:
            os.rename(old_filepath, new_filepath)
        except FileExistsError:
            os.remove(new_filepath)
            os.rename(old_filepath, new_filepath)
    
# Remove compositor nodes created by the script
def remove_compositor_nodes():
    for node in compositor.nodes:
        if node.type != 'R_LAYERS' and node.type != 'COMPOSITE' and node.type != 'REROUTE' and node.type != 'VIEWER':
            compositor.nodes.remove(node)
        
# Restores object names
def restore_names(obj):
    if obj.name in original_names:
        obj.name = original_names[obj.name]

# Selects the first uv channel
def select_first_uv_channel(obj):
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
            return int(bake_resolution)
    return int(default_resolution)
    
# Sets up the compositor nodes for denoising and saving the
# square root of the image's RGB values
def sqrt_denoise_and_save(obj, current_map):
    image_node = compositor.nodes.new(type='CompositorNodeImage')
    image_node.image = bpy.data.images.get("bakemap")
    file_output_node = compositor.nodes.new('CompositorNodeOutputFile')
    file_output_node.directory = path
    file_output_node.format.media_type = 'IMAGE'
    file_output_node.file_output_items.new(socket_type='RGBA', name="Image")
    file_output_node.file_name = obj.name + current_map
    denoise_node = compositor.nodes.new(type='CompositorNodeDenoise')
    denoise_node.inputs["HDR"].default_value = False
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
    bpy.data.collections.remove(temporary_collection)

# Set Sun strength to 12, and background strength, emission strength, and total scene light bounces to 0
def change_light_setup():
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
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT'})
    if savefile == True:
        bakemap.filepath_raw = path + obj.name + "_shadowmap.png"
        bakemap.save()

# Restores original light setup
def restore_light_setup():
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
    bpy.context.scene.view_settings.view_transform = original_settings["view_transform"]
    bpy.context.scene.render.resolution_percentage = original_settings["resolution_percentage"]
    bpy.context.scene.render.bake.margin = original_settings["bake_margin"]
    bpy.context.scene.render.bake.margin_type = original_settings["bake_margin_type"]

# Removes bakemap texture, its image node, and re-enables all normals
def remove_bakemap():
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
