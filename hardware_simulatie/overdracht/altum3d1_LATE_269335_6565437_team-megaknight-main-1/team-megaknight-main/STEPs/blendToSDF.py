"""
Blender to Gazebo SDF Exporter
For Blender 5.1

Exports each mesh individually and generates a complete Gazebo model folder with:
- model.config
- model.sdf
- meshes/ folder with visual and collision meshes
- Principled BSDF materials
- Lights (point, spot, sun/directional)

Naming convention:
- Objects ending with '_col' are treated as collision meshes
- They are paired with visual meshes of the same name (without '_col')
- Objects without a '_col' counterpart use themselves as collision

Usage:
1. Open in Blender's Text Editor
2. Adjust the settings in the CONFIG section below
3. Run the script (Alt+P or Run Script button)
"""

import bpy
import bmesh
import re
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
from pathlib import Path
from mathutils import Matrix, Vector

# ============================================================================
# CONFIG - Adjust these settings
# ============================================================================

MODEL_NAME = "remeshes_gazebo"  # Name of the model
EXPORT_PATH = r"C:\Users\Frid\Desktop\Maps\School\TI-S4\team-megaknight\STEPs\SDFs"  # Where to export (will create subfolder)
MESH_FORMAT = "obj"  # Options: "stl" (recommended), "obj", "glb", "dae"
SDF_VERSION = "1.9"  # SDF version for Gazebo

#   0.001  = Blender units are millimeters (mm)
UNIT_SCALE = 0.001  # Default: millimeters to meters

# Export settings
APPLY_MODIFIERS = True
EXPORT_SELECTED_ONLY = True  # Set True to only export selected objects
EXPORT_LIGHTS = True  # Export lights from scene
EXPORT_MATERIALS = True  # Export Principled BSDF materials

# ============================================================================
# SCRIPT - Don't modify below unless you know what you're doing
# ============================================================================


def sanitize_name(name):
    """Convert name to a valid filename/XML identifier."""
    sanitized = re.sub(r'[^\w\-]', '_', name)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_')
    return sanitized


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def has_geometry(obj):
    """Check if mesh object has actual geometry (vertices/faces)."""
    if obj.type != 'MESH':
        return False
    mesh = obj.data
    return len(mesh.vertices) > 0 and len(mesh.polygons) > 0


def get_principled_bsdf(obj):
    """
    Extract Principled BSDF material properties from an object.
    Returns dict with color values or None if no valid material.
    """
    if not obj.data.materials:
        return None

    mat = obj.data.materials[0]
    if not mat or not mat.use_nodes:
        return None

    # Find Principled BSDF node
    principled = None
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled = node
            break

    if not principled:
        return None

    # Helper to get input value (handles both direct values and linked nodes)
    def get_input(name, default):
        inp = principled.inputs.get(name)
        if inp is None:
            return default
        # If connected to another node, try to get default_value anyway
        if hasattr(inp, 'default_value'):
            return inp.default_value
        return default

    # Extract colors and properties
    base_color = get_input('Base Color', (0.8, 0.8, 0.8, 1.0))
    metallic = get_input('Metallic', 0.0)
    roughness = get_input('Roughness', 0.5)
    emission = get_input('Emission Color', (0.0, 0.0, 0.0, 1.0))
    emission_strength = get_input('Emission Strength', 0.0)

    # Convert to RGBA tuples
    if hasattr(base_color, '__iter__'):
        base_color = tuple(base_color)[:4]
    else:
        base_color = (base_color, base_color, base_color, 1.0)

    if hasattr(emission, '__iter__'):
        emission = tuple(emission)[:4]
    else:
        emission = (0.0, 0.0, 0.0, 1.0)

    # Calculate specular from metallic/roughness (simplified)
    spec_intensity = (1.0 - roughness) * 0.5
    if metallic > 0.5:
        specular = (base_color[0] * spec_intensity,
                    base_color[1] * spec_intensity,
                    base_color[2] * spec_intensity, 1.0)
    else:
        specular = (spec_intensity, spec_intensity, spec_intensity, 1.0)

    # Ambient is a dimmed version of base color
    ambient = (base_color[0] * 0.3, base_color[1] * 0.3, base_color[2] * 0.3, 1.0)

    # Emissive with strength
    emissive = (emission[0] * emission_strength,
                emission[1] * emission_strength,
                emission[2] * emission_strength, 1.0)

    return {
        'ambient': ambient,
        'diffuse': base_color,
        'specular': specular,
        'emissive': emissive,
    }


def get_mesh_pairs(objects):
    """
    Organize objects into visual/collision pairs.
    Objects ending with '_col' are collision meshes.
    """
    pairs = defaultdict(lambda: {"visual": None, "collision": None, "visual_name": None, "collision_name": None})

    for obj in objects:
        if obj.type != 'MESH':
            continue

        if not has_geometry(obj):
            print(f"  Skipping '{obj.name}' - no geometry")
            continue

        name = obj.name

        if name.endswith('_col'):
            base_name = name[:-4]
            sanitized = sanitize_name(base_name)
            pairs[sanitized]["collision"] = obj
            pairs[sanitized]["collision_name"] = name
        else:
            sanitized = sanitize_name(name)
            pairs[sanitized]["visual"] = obj
            pairs[sanitized]["visual_name"] = name

    return pairs


def get_lights(objects):
    """Extract light objects and their properties."""
    lights = []

    for obj in objects:
        if obj.type != 'LIGHT':
            continue

        light_data = obj.data
        light_info = {
            'name': sanitize_name(obj.name),
            'original_name': obj.name,
            'location': obj.location,
            'rotation': obj.rotation_euler,
            'color': tuple(light_data.color),
            'energy': light_data.energy,
        }

        # Map Blender light types to Gazebo
        if light_data.type == 'POINT':
            light_info['type'] = 'point'
            light_info['range'] = getattr(light_data, 'shadow_soft_size', 10.0) * 10
        elif light_data.type == 'SUN':
            light_info['type'] = 'directional'
            # Direction is -Z in light's local space
            direction = obj.matrix_world.to_3x3() @ Vector((0, 0, -1))
            light_info['direction'] = tuple(direction)
        elif light_data.type == 'SPOT':
            light_info['type'] = 'spot'
            light_info['range'] = getattr(light_data, 'shadow_soft_size', 10.0) * 10
            light_info['inner_angle'] = light_data.spot_size * 0.5 * 0.8  # 80% of outer
            light_info['outer_angle'] = light_data.spot_size * 0.5
            direction = obj.matrix_world.to_3x3() @ Vector((0, 0, -1))
            light_info['direction'] = tuple(direction)
        elif light_data.type == 'AREA':
            # Approximate area light as point light
            light_info['type'] = 'point'
            light_info['range'] = 20.0
            print(f"  Note: Area light '{obj.name}' exported as point light")
        else:
            continue

        lights.append(light_info)

    return lights


def export_mesh(obj, filepath, mesh_format):
    """Export a single mesh object to the specified format."""
    original_selection = [o for o in bpy.context.selected_objects]
    original_active = bpy.context.view_layer.objects.active

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        if mesh_format == "dae":
            try:
                bpy.ops.wm.collada_export(
                    filepath=filepath,
                    selected=True,
                    apply_modifiers=APPLY_MODIFIERS,
                )
            except AttributeError:
                try:
                    bpy.ops.export_scene.collada(
                        filepath=filepath,
                        selected=True,
                        apply_modifiers=APPLY_MODIFIERS,
                    )
                except:
                    print(f"  Warning: Collada not available, using glTF instead")
                    gltf_path = filepath.replace('.dae', '.glb')
                    bpy.ops.export_scene.gltf(
                        filepath=gltf_path,
                        use_selection=True,
                        export_apply=APPLY_MODIFIERS,
                    )
                    return gltf_path
        elif mesh_format == "stl":
            try:
                bpy.ops.wm.stl_export(
                    filepath=filepath,
                    export_selected_objects=True,
                    apply_modifiers=APPLY_MODIFIERS,
                    forward_axis='Y',
                    up_axis='Z',
                )
            except (AttributeError, TypeError):
                try:
                    bpy.ops.export_mesh.stl(
                        filepath=filepath,
                        use_selection=True,
                        use_mesh_modifiers=APPLY_MODIFIERS,
                        axis_forward='Y',
                        axis_up='Z',
                    )
                except Exception as e:
                    print(f"  ERROR exporting {obj.name}: {e}")
                    return None
        elif mesh_format == "obj":
            try:
                bpy.ops.wm.obj_export(
                    filepath=filepath,
                    export_selected_objects=True,
                    apply_modifiers=APPLY_MODIFIERS,
                )
            except AttributeError:
                bpy.ops.export_scene.obj(
                    filepath=filepath,
                    use_selection=True,
                    use_mesh_modifiers=APPLY_MODIFIERS,
                )
        elif mesh_format == "glb" or mesh_format == "gltf":
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                use_selection=True,
                export_apply=APPLY_MODIFIERS,
            )
        else:
            raise ValueError(f"Unsupported mesh format: {mesh_format}")

    finally:
        bpy.ops.object.select_all(action='DESELECT')
        for o in original_selection:
            o.select_set(True)
        if original_active:
            bpy.context.view_layer.objects.active = original_active

    return filepath


def create_model_config(model_name, author="Blender Export"):
    """Create model.config XML content."""
    model = ET.Element("model")

    name = ET.SubElement(model, "name")
    name.text = model_name

    version = ET.SubElement(model, "version")
    version.text = "1.0"

    sdf_elem = ET.SubElement(model, "sdf", version=SDF_VERSION)
    sdf_elem.text = "model.sdf"

    author_elem = ET.SubElement(model, "author")
    author_name = ET.SubElement(author_elem, "name")
    author_name.text = author

    description = ET.SubElement(model, "description")
    description.text = f"Model exported from Blender"

    return prettify_xml(model)


def add_material_to_visual(visual_elem, material_props):
    """Add SDF material element to a visual."""
    if not material_props:
        return

    material = ET.SubElement(visual_elem, "material")

    # Ambient color
    ambient = ET.SubElement(material, "ambient")
    ambient.text = f"{material_props['ambient'][0]:.4f} {material_props['ambient'][1]:.4f} {material_props['ambient'][2]:.4f} {material_props['ambient'][3]:.4f}"

    # Diffuse color
    diffuse = ET.SubElement(material, "diffuse")
    diffuse.text = f"{material_props['diffuse'][0]:.4f} {material_props['diffuse'][1]:.4f} {material_props['diffuse'][2]:.4f} {material_props['diffuse'][3]:.4f}"

    # Specular color
    specular = ET.SubElement(material, "specular")
    specular.text = f"{material_props['specular'][0]:.4f} {material_props['specular'][1]:.4f} {material_props['specular'][2]:.4f} {material_props['specular'][3]:.4f}"

    # Emissive color
    emissive = ET.SubElement(material, "emissive")
    emissive.text = f"{material_props['emissive'][0]:.4f} {material_props['emissive'][1]:.4f} {material_props['emissive'][2]:.4f} {material_props['emissive'][3]:.4f}"


def add_light_to_model(model_elem, light_info, unit_scale):
    """Add a light element inside a link to the SDF model."""
    # Lights must be inside a link in SDF models
    link = ET.SubElement(model_elem, "link", name=f"{light_info['name']}_link")

    # Link pose
    loc = light_info['location']
    rot = light_info['rotation']
    link_pose = ET.SubElement(link, "pose")
    link_pose.text = f"{loc.x * unit_scale:.6f} {loc.y * unit_scale:.6f} {loc.z * unit_scale:.6f} {rot.x:.6f} {rot.y:.6f} {rot.z:.6f}"

    # Light element inside the link (pose relative to link, so 0 0 0)
    light = ET.SubElement(link, "light", name=light_info['name'], type=light_info['type'])

    # Light pose relative to link (identity)
    light_pose = ET.SubElement(light, "pose")
    light_pose.text = "0 0 0 0 0 0"

    # Cast shadows
    cast_shadows = ET.SubElement(light, "cast_shadows")
    cast_shadows.text = "true"

    # Diffuse color (light color)
    color = light_info['color']
    intensity = min(light_info['energy'] / 1000.0, 1.0)  # Normalize energy

    diffuse = ET.SubElement(light, "diffuse")
    diffuse.text = f"{color[0] * intensity:.4f} {color[1] * intensity:.4f} {color[2] * intensity:.4f} 1"

    specular = ET.SubElement(light, "specular")
    specular.text = f"{color[0] * intensity * 0.5:.4f} {color[1] * intensity * 0.5:.4f} {color[2] * intensity * 0.5:.4f} 1"

    # Attenuation (for point and spot lights)
    if light_info['type'] in ('point', 'spot'):
        attenuation = ET.SubElement(light, "attenuation")
        range_elem = ET.SubElement(attenuation, "range")
        range_elem.text = f"{light_info.get('range', 10.0) * unit_scale:.4f}"
        constant = ET.SubElement(attenuation, "constant")
        constant.text = "0.5"
        linear = ET.SubElement(attenuation, "linear")
        linear.text = "0.01"
        quadratic = ET.SubElement(attenuation, "quadratic")
        quadratic.text = "0.001"

    # Direction (for directional and spot lights)
    if light_info['type'] in ('directional', 'spot'):
        direction = ET.SubElement(light, "direction")
        d = light_info['direction']
        direction.text = f"{d[0]:.6f} {d[1]:.6f} {d[2]:.6f}"

    # Spot light specific
    if light_info['type'] == 'spot':
        spot = ET.SubElement(light, "spot")
        inner = ET.SubElement(spot, "inner_angle")
        inner.text = f"{light_info['inner_angle']:.4f}"
        outer = ET.SubElement(spot, "outer_angle")
        outer.text = f"{light_info['outer_angle']:.4f}"
        falloff = ET.SubElement(spot, "falloff")
        falloff.text = "1.0"


def create_sdf(model_name, mesh_pairs, lights, mesh_format, unit_scale, export_materials):
    """Create model.sdf XML content."""
    sdf = ET.Element("sdf", version=SDF_VERSION)
    model = ET.SubElement(sdf, "model", name=model_name)

    # Static model
    static = ET.SubElement(model, "static")
    static.text = "true"

    # Add lights
    for light_info in lights:
        add_light_to_model(model, light_info, unit_scale)

    # Add mesh links
    for link_name, pair in mesh_pairs.items():
        visual_obj = pair["visual"]
        collision_obj = pair["collision"]

        if visual_obj is None:
            if collision_obj is not None:
                print(f"Warning: '{pair['collision_name']}' has no visual counterpart, skipping...")
            continue

        # Create link
        link = ET.SubElement(model, "link", name=f"{link_name}_link")

        # Get transform
        loc = visual_obj.location
        rot = visual_obj.rotation_euler

        scaled_x = loc.x * unit_scale
        scaled_y = loc.y * unit_scale
        scaled_z = loc.z * unit_scale

        # Pose
        pose = ET.SubElement(link, "pose")
        pose.text = f"{scaled_x:.6f} {scaled_y:.6f} {scaled_z:.6f} {rot.x:.6f} {rot.y:.6f} {rot.z:.6f}"

        # Visual element
        visual = ET.SubElement(link, "visual", name=f"{link_name}_visual")
        visual_geom = ET.SubElement(visual, "geometry")
        visual_mesh = ET.SubElement(visual_geom, "mesh")
        visual_uri = ET.SubElement(visual_mesh, "uri")
        visual_uri.text = f"meshes/{link_name}.{mesh_format}"

        if unit_scale != 1.0:
            visual_scale = ET.SubElement(visual_mesh, "scale")
            visual_scale.text = f"{unit_scale} {unit_scale} {unit_scale}"

        # Add material from Principled BSDF
        if export_materials:
            material_props = get_principled_bsdf(visual_obj)
            if material_props:
                add_material_to_visual(visual, material_props)

        # Collision element
        collision = ET.SubElement(link, "collision", name=f"{link_name}_collision")
        collision_geom = ET.SubElement(collision, "geometry")
        collision_mesh = ET.SubElement(collision_geom, "mesh")
        collision_uri = ET.SubElement(collision_mesh, "uri")

        if collision_obj is not None:
            collision_uri.text = f"meshes/{link_name}_col.{mesh_format}"
        else:
            collision_uri.text = f"meshes/{link_name}.{mesh_format}"

        if unit_scale != 1.0:
            collision_scale = ET.SubElement(collision_mesh, "scale")
            collision_scale.text = f"{unit_scale} {unit_scale} {unit_scale}"

    return prettify_xml(sdf)


def main():
    """Main export function."""
    print("=" * 60)
    print("Blender to Gazebo SDF Exporter")
    print("=" * 60)

    # Create export directories
    model_path = Path(EXPORT_PATH) / MODEL_NAME
    meshes_path = model_path / "meshes"
    meshes_path.mkdir(parents=True, exist_ok=True)

    print(f"Export path: {model_path}")
    print(f"Unit scale: {UNIT_SCALE} (Blender units × {UNIT_SCALE} = meters)")
    print(f"Export materials: {EXPORT_MATERIALS}")
    print(f"Export lights: {EXPORT_LIGHTS}")

    # Get objects to export
    if EXPORT_SELECTED_ONLY:
        all_objects = list(bpy.context.selected_objects)
    else:
        all_objects = list(bpy.data.objects)

    mesh_objects = [obj for obj in all_objects if obj.type == 'MESH']
    light_objects = [obj for obj in all_objects if obj.type == 'LIGHT'] if EXPORT_LIGHTS else []

    if not mesh_objects and not light_objects:
        print("ERROR: No mesh or light objects found to export!")
        return

    print(f"Found {len(mesh_objects)} mesh objects")
    print(f"Found {len(light_objects)} light objects")

    # Organize meshes
    print("\nAnalyzing meshes...")
    mesh_pairs = get_mesh_pairs(mesh_objects)
    print(f"Organized into {len(mesh_pairs)} link(s)")

    # Get lights
    lights = []
    if EXPORT_LIGHTS and light_objects:
        print("\nAnalyzing lights...")
        lights = get_lights(light_objects)
        print(f"Found {len(lights)} exportable lights")

    # Export meshes
    print("\nExporting meshes...")
    exported_count = 0
    skipped_count = 0

    for link_name, pair in mesh_pairs.items():
        visual_obj = pair["visual"]
        collision_obj = pair["collision"]

        if visual_obj:
            visual_path = str(meshes_path / f"{link_name}.{MESH_FORMAT}")
            print(f"  Visual: {pair['visual_name']} -> {link_name}.{MESH_FORMAT}")
            export_mesh(visual_obj, visual_path, MESH_FORMAT)
            exported_count += 1
        else:
            skipped_count += 1

        if collision_obj:
            collision_path = str(meshes_path / f"{link_name}_col.{MESH_FORMAT}")
            print(f"  Collision: {pair['collision_name']} -> {link_name}_col.{MESH_FORMAT}")
            export_mesh(collision_obj, collision_path, MESH_FORMAT)
            exported_count += 1

    # Create model.config
    print("\nGenerating model.config...")
    config_content = create_model_config(MODEL_NAME)
    config_path = model_path / "model.config"
    with open(config_path, 'w') as f:
        f.write(config_content)

    # Create model.sdf
    print("Generating model.sdf...")
    sdf_content = create_sdf(MODEL_NAME, mesh_pairs, lights, MESH_FORMAT, UNIT_SCALE, EXPORT_MATERIALS)
    sdf_path = model_path / "model.sdf"
    with open(sdf_path, 'w') as f:
        f.write(sdf_content)

    print("\n" + "=" * 60)
    print("EXPORT COMPLETE!")
    print("=" * 60)
    print(f"Model folder: {model_path}")
    print(f"Meshes exported: {exported_count}")
    print(f"Lights exported: {len(lights)}")
    if skipped_count > 0:
        print(f"Skipped (no visual): {skipped_count}")
    print(f"\nFiles created:")
    print(f"  - model.config")
    print(f"  - model.sdf")
    print(f"  - meshes/*.{MESH_FORMAT}")
    print("\nTo use in Gazebo:")
    print(f"  1. Copy '{MODEL_NAME}' folder to your Gazebo models directory")
    print(f"  2. Or set GZ_SIM_RESOURCE_PATH={model_path.parent}")
    print("=" * 60)


# Run the script
if __name__ == "__main__":
    main()
