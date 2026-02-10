import bpy
import os

os.system('cls')
path = "C:/Users/Colin/Desktop/Sega/Modding/Projects/Render Test/GITextures/"
render_list = "C:/Users/Colin/Desktop/Sega/Modding/Projects/Render Test/RenderList.txt"
use_render_list = True
use_denoise = True
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
    ShowMessageBox("No issues found", icon = 'CHECKMARK')
else:
    ShowMessageBox(message=issues_found)
