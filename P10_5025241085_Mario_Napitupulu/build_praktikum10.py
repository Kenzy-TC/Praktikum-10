import bpy
import math
import os
import random
import shutil
import struct
import zlib
from array import array
from mathutils import Vector


ROOT = os.path.dirname(os.path.abspath(__file__))
P9_BLEND = r"E:\Grafkom\Praktikum 9\P09_5025241085_Mario_Napitupulu\P09_02_Kotak_Perkakas.blend"
EXT_BLEND = os.path.join(ROOT, "external_assets", "industrial_pipe_lamp_1k.blend")
EXT_TEX = os.path.join(ROOT, "external_assets", "textures")
TEX_DIR = os.path.join(ROOT, "textures")
POLY_TEX_DIR = os.path.join(TEX_DIR, "polyhaven")
SHOT_DIR = os.path.join(ROOT, "screenshots")
BLEND_OUT = os.path.join(ROOT, "P10_5025241085_Mario_Napitupulu.blend")
TABLE_TOP = 0.64
MODEL_SCALE = 0.26
LAMP_SCALE = 2.0

os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(POLY_TEX_DIR, exist_ok=True)
os.makedirs(SHOT_DIR, exist_ok=True)


def texture_path(name):
    return os.path.join(TEX_DIR, name)


def ext_texture(name):
    return os.path.join(EXT_TEX, name)


def make_toolbox_textures():
    size = 512

    def save_map(filename, name, color_fn, color_space="Non-Color"):
        raw_rows = bytearray()
        for y in range(size):
            v = y / float(size - 1)
            raw_rows.append(0)
            for x in range(size):
                u = x / float(size - 1)
                r, g, b = color_fn(u, v, x, y)
                raw_rows.extend((int(max(0.0, min(1.0, r)) * 255.0 + 0.5), int(max(0.0, min(1.0, g)) * 255.0 + 0.5), int(max(0.0, min(1.0, b)) * 255.0 + 0.5)))
        def png_chunk(kind, payload):
            body = kind + payload
            return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)
        filepath = texture_path(filename)
        png = b"\x89PNG\r\n\x1a\n"
        png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        png += png_chunk(b"IDAT", zlib.compress(bytes(raw_rows), 8))
        png += png_chunk(b"IEND", b"")
        with open(filepath, "wb") as stream:
            stream.write(png)
        image = bpy.data.images.load(filepath, check_existing=False)
        image.name = name
        image.colorspace_settings.name = color_space
        image.filepath = filepath
        return image

    def hash_value(x, y):
        value = math.sin(x * 127.1 + y * 311.7) * 43758.5453123
        return value - math.floor(value)

    def base_color(u, v, x, y):
        broad = 0.018 * math.sin(u * 13.0 + math.sin(v * 9.0))
        grain = 0.006 * math.sin(u * 180.0 + 2.0 * math.sin(v * 23.0))
        mottling = 0.009 * math.sin((u + v) * 31.0) * math.sin(v * 27.0)
        chip = hash_value(x // 2, y // 2) > 0.997
        value = broad + grain + mottling
        if chip:
            return (0.035, 0.055, 0.060)
        return (max(0.02, 0.09 + value), max(0.02, 0.25 + value * 1.8), max(0.02, 0.29 + value * 2.0))

    def roughness(u, v, x, y):
        n = 0.045 * math.sin(u * 17.0 + math.sin(v * 31.0)) + 0.025 * math.sin(v * 56.0)
        if hash_value(x // 3, y // 3) > 0.997:
            n += 0.24
        val = min(0.78, max(0.30, 0.46 + n))
        return (val, val, val)

    def metallic(u, v, x, y):
        scratch = hash_value(x // 2, y // 2) > 0.9975
        val = 0.74 if scratch else 0.06
        return (val, val, val)

    def ao(u, v, x, y):
        mottling = 0.025 * math.sin(u * 19.0 + math.sin(v * 13.0)) * math.sin(v * 17.0 + math.sin(u * 7.0))
        val = min(0.97, max(0.82, 0.90 + mottling))
        return (val, val, val)

    def normal(u, v, x, y):
        nx = 0.075 * math.sin(u * 250.0 + 2.0 * math.sin(v * 23.0))
        ny = 0.065 * math.cos(v * 235.0 + 1.5 * math.sin(u * 17.0))
        nz = 1.0
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        return (0.5 + nx / length * 0.5, 0.5 + ny / length * 0.5, 0.5 + nz / length * 0.5)

    def emission(u, v, x, y):
        # Small amber hash marks on the shell; the separate status objects remain the brightest LEDs.
        stripe = (0.39 < v < 0.405 and 0.17 < u < 0.30 and int(u * 90.0) % 3 == 0)
        val = 1.0 if stripe else 0.0
        return (1.0 * val, 0.31 * val, 0.035 * val)

    return {
        "base": save_map("kestrel09_basecolor.png", "Kestrel09 | Base Color", base_color, "sRGB"),
        "ao": save_map("kestrel09_ao.png", "Kestrel09 | Ambient Occlusion", ao),
        "rough": save_map("kestrel09_roughness.png", "Kestrel09 | Roughness", roughness),
        "metal": save_map("kestrel09_metallic.png", "Kestrel09 | Metallic", metallic),
        "normal": save_map("kestrel09_normal.png", "Kestrel09 | Normal", normal),
        "emission": save_map("kestrel09_emission.png", "Kestrel09 | Emission", emission, "sRGB"),
    }


def get_image(path, name, color_space):
    image = bpy.data.images.load(path, check_existing=True)
    image.name = name
    image.colorspace_settings.name = color_space
    image.filepath = os.path.abspath(path)
    return image


def clear_and_link(nodes, links):
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (420, 120)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (120, 120)
    links.new(bsdf.outputs[0], output.inputs["Surface"])
    return bsdf, output


def build_pbr_material(name, maps, emission_strength=0.0, ao_factor=0.38):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf, _ = clear_and_link(nodes, links)
    bsdf.inputs["Metallic"].default_value = 0.05
    bsdf.inputs["Roughness"].default_value = 0.45

    uv = nodes.new("ShaderNodeTexCoord")
    uv.label = "UV mapping"
    uv.location = (-1120, 40)

    def image_node(key, label, loc, color_space):
        image = maps[key]
        image.colorspace_settings.name = color_space
        node = nodes.new("ShaderNodeTexImage")
        node.image = image
        node.label = label
        node.location = loc
        links.new(uv.outputs["UV"], node.inputs["Vector"])
        return node

    base = image_node("base", "Base Color | sRGB", (-870, 360), "sRGB")
    ao = image_node("ao", "Ambient Occlusion | Non-Color", (-870, 100), "Non-Color")
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = ao_factor
    multiply.label = "Subtle AO shading"
    multiply.location = (-560, 350)
    links.new(base.outputs["Color"], multiply.inputs[1])
    links.new(ao.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], bsdf.inputs["Base Color"])

    rough = image_node("rough", "Roughness | Non-Color", (-870, -140), "Non-Color")
    metal = image_node("metal", "Metallic | Non-Color", (-870, -390), "Non-Color")
    normal = image_node("normal", "Normal | Non-Color", (-870, -650), "Non-Color")
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.label = "Tangent-space Normal"
    normal_map.location = (-560, -620)
    normal_map.inputs["Strength"].default_value = 0.42
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(metal.outputs["Color"], bsdf.inputs["Metallic"])
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    emission = image_node("emission", "Emission Mask | sRGB", (-870, -900), "sRGB")
    emission_socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission_socket:
        links.new(emission.outputs["Color"], emission_socket)
    strength_socket = bsdf.inputs.get("Emission Strength")
    if strength_socket:
        strength_socket.default_value = emission_strength
    return material


def build_lamp_material():
    maps = {
        "base": get_image(ext_texture("industrial_pipe_lamp_diff_1k.jpg"), "Poly Haven | Lamp Diffuse", "sRGB"),
        "ao": get_image(ext_texture("industrial_pipe_lamp_ao_1k.exr"), "Poly Haven | Lamp AO", "Non-Color"),
        "metal": get_image(ext_texture("industrial_pipe_lamp_metal_1k.exr"), "Poly Haven | Lamp Metallic", "Non-Color"),
        "normal": get_image(ext_texture("industrial_pipe_lamp_nor_gl_1k.exr"), "Poly Haven | Lamp Normal GL", "Non-Color"),
        "rough": get_image(ext_texture("industrial_pipe_lamp_rough_1k.exr"), "Poly Haven | Lamp Roughness", "Non-Color"),
        "emission": get_image(ext_texture("industrial_pipe_lamp_emission_1k.png"), "Poly Haven | Lamp Emission", "sRGB"),
    }
    return build_pbr_material("External | Industrial Pipe Lamp | PBR", maps, emission_strength=1.6, ao_factor=0.36)


def build_toolbox_material(maps):
    images = {
        "base": maps["base"],
        "rough": maps["rough"],
        "metal": maps["metal"],
        "normal": maps["normal"],
        "emission": maps["emission"],
        "ao": maps["ao"],
    }
    return build_pbr_material("Kestrel-09 | Hand-made UV PBR", images, emission_strength=0.55, ao_factor=0.10)


def simple_material(name, color, metallic=0.0, roughness=0.45, emission=None, emission_strength=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if socket:
            socket.default_value = (*emission, 1.0)
        strength = bsdf.inputs.get("Emission Strength")
        if strength:
            strength.default_value = emission_strength
    return material


def set_object_material(obj, material):
    if obj.type != "MESH":
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def apply_object_scale(obj):
    if obj.type != "MESH":
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def object_bounds_z(objects):
    bpy.context.view_layer.update()
    values = []
    for obj in objects:
        if obj.type not in {"MESH", "CURVE", "FONT"}:
            continue
        for corner in obj.bound_box:
            values.append((obj.matrix_world @ Vector(corner)).z)
    return min(values) if values else 0.0


def set_edge_seams(mesh):
    edge_faces = {}
    for polygon in mesh.polygons:
        for key in polygon.edge_keys:
            edge_faces.setdefault(tuple(sorted(key)), []).append(polygon)
    for edge in mesh.edges:
        linked = edge_faces.get(tuple(sorted(edge.vertices)), [])
        if len(linked) != 2:
            edge.use_seam = True
        else:
            edge.use_seam = linked[0].normal.angle(linked[1].normal) > math.radians(42.0)


def uv_coordinates(mesh):
    layer = mesh.uv_layers.active
    return [(float(item.uv.x), float(item.uv.y)) for item in layer.data]


def draw_line(buffer, size, x0, y0, x1, y1, color, thickness=2):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for oy in range(-thickness // 2, thickness // 2 + 1):
            for ox in range(-thickness // 2, thickness // 2 + 1):
                xx = x0 + ox
                yy = y0 + oy
                if 0 <= xx < size and 0 <= yy < size:
                    i = (yy * size + xx) * 4
                    buffer[i] = color[0]
                    buffer[i + 1] = color[1]
                    buffer[i + 2] = color[2]
                    buffer[i + 3] = 1.0
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def save_uv_snapshot(obj, filepath, coords=None, seams=False, fit=False):
    size = 768
    margin = 42
    mesh = obj.data
    if coords is None:
        coords = uv_coordinates(mesh)
    us = [p[0] for p in coords]
    vs = [p[1] for p in coords]
    min_u, max_u = min(us), max(us)
    min_v, max_v = min(vs), max(vs)
    if fit:
        span = max(max_u - min_u, max_v - min_v, 1e-6)
        scale = (size - margin * 2) / span

        def xy(uv):
            return (int(margin + (uv[0] - min_u) * scale), int(margin + (uv[1] - min_v) * scale))
    else:
        def xy(uv):
            return (int(margin + uv[0] * (size - margin * 2)), int(margin + uv[1] * (size - margin * 2)))

    buffer = array("f", [0.035, 0.050, 0.065, 1.0]) * (size * size)
    for step in range(1, 10):
        pos = int(margin + step * (size - margin * 2) / 10.0)
        draw_line(buffer, size, pos, margin, pos, size - margin, (0.12, 0.16, 0.18), 1)
        draw_line(buffer, size, margin, pos, size - margin, pos, (0.12, 0.16, 0.18), 1)

    edge_map = {tuple(sorted(edge.vertices)): edge for edge in mesh.edges}
    layer = mesh.uv_layers.active
    for polygon in mesh.polygons:
        loops = list(polygon.loop_indices)
        for i, loop_index in enumerate(loops):
            next_index = loops[(i + 1) % len(loops)]
            v0 = mesh.loops[loop_index].vertex_index
            v1 = mesh.loops[next_index].vertex_index
            uv0 = coords[loop_index]
            uv1 = coords[next_index]
            x0, y0 = xy(uv0)
            x1, y1 = xy(uv1)
            edge = edge_map.get(tuple(sorted((v0, v1))))
            color = (0.98, 0.25, 0.12) if seams and edge and edge.use_seam else (0.70, 0.82, 0.86)
            draw_line(buffer, size, x0, y0, x1, y1, color, 2)

    image = bpy.data.images.new("UV proof | " + os.path.basename(filepath), width=size, height=size, alpha=False)
    image.pixels.foreach_set(buffer)
    image.filepath_raw = filepath
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def unwrap_all_meshes(toolbox_objects):
    body = bpy.data.objects.get("Crate_Body")
    for obj in toolbox_objects:
        if obj.type != "MESH" or not obj.data.vertices:
            continue
        set_edge_seams(obj.data)
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UV_Kestrel_Manual")
        obj.data.uv_layers.active.name = "UV_Kestrel_Manual"
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.025)
        bpy.context.view_layer.update()
        bpy.ops.uv.pack_islands(rotate=True, margin=0.035)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(False)
    if body and body.data.uv_layers.active:
        save_uv_snapshot(body, os.path.join(SHOT_DIR, "02_seam.png"), seams=True, fit=False)
        save_uv_snapshot(body, os.path.join(SHOT_DIR, "03_uv.png"), seams=False, fit=False)
    return body


def make_texture_surface_material():
    mat = simple_material("Stage | Walnut worktop", (0.10, 0.038, 0.014), metallic=0.08, roughness=0.39)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-700, 80)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-500, 160)
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 4.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-260, 180)
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.045, 0.016, 0.008, 1.0)
    ramp.color_ramp.elements[1].position = 0.79
    ramp.color_ramp.elements[1].color = (0.20, 0.075, 0.024, 1.0)
    wave = nodes.new("ShaderNodeTexWave")
    wave.location = (-490, -100)
    wave.inputs["Scale"].default_value = 7.0
    wave.inputs["Distortion"].default_value = 1.2
    bump = nodes.new("ShaderNodeBump")
    bump.location = (-220, -80)
    bump.inputs["Strength"].default_value = 0.07
    bump.inputs["Distance"].default_value = 0.012
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(texcoord.outputs["Generated"], wave.inputs["Vector"])
    links.new(wave.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def add_cube(name, location, dimensions, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel:
        modifier = obj.modifiers.new("Soft machined edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 4
        modifier.profile = 0.5
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_area(name, location, target, power, color, size, shape="DISK", size_y=None):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = power
    data.color = color
    data.shape = shape
    data.size = size
    if shape == "RECTANGLE" and size_y:
        data.size_y = size_y
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, target)
    return obj


def add_text(name, body, location, size, material, rotation=(math.pi / 2.0, 0.0, 0.0)):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.0007
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    curve.materials.append(material)
    return obj


def create_stage():
    scene = bpy.context.scene
    floor_mat = simple_material("Stage | Deep blue backdrop", (0.012, 0.024, 0.038), metallic=0.10, roughness=0.58)
    dark_metal = simple_material("Stage | Graphite frame", (0.025, 0.045, 0.056), metallic=0.72, roughness=0.31)
    brass = simple_material("Stage | Warm brass inlay", (0.42, 0.20, 0.045), metallic=0.78, roughness=0.24)
    text_mat = simple_material("Stage | Engraving", (0.76, 0.49, 0.15), metallic=0.25, roughness=0.33, emission=(0.22, 0.075, 0.012), emission_strength=0.35)
    worktop = make_texture_surface_material()

    bpy.ops.mesh.primitive_plane_add(size=200.0, location=(0.0, 0.0, -0.015))
    ground = bpy.context.object
    ground.name = "Infinite studio ground"
    ground.data.materials.append(floor_mat)

    add_cube("Workbench | walnut top", (0.0, 0.0, 0.55), (3.45, 2.45, 0.18), worktop, bevel=0.055)
    for x in (-1.38, 1.38):
        for y in (-0.92, 0.92):
            add_cube("Workbench | leg", (x, y, 0.22), (0.16, 0.16, 0.50), dark_metal, bevel=0.025)
    add_cube("Workbench | front rail", (0.0, -0.95, 0.35), (2.78, 0.12, 0.20), dark_metal, bevel=0.025)
    add_cube("Workbench | rear rail", (0.0, 0.95, 0.35), (2.78, 0.12, 0.20), dark_metal, bevel=0.025)
    add_cube("Workbench | brass front accent", (0.0, -1.236, 0.55), (1.66, 0.018, 0.018), brass, bevel=0.006)
    add_cube("Workbench | title plaque", (0.0, -1.242, 0.55), (1.38, 0.025, 0.14), dark_metal, bevel=0.018)
    add_text("Workbench | engraved title", "KESTREL-09  /  MATERIAL STUDY", (-0.60, -1.259, 0.525), 0.067, text_mat)

    world = scene.world or bpy.data.worlds.new("P10 | Midnight workshop")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.012, 0.026, 0.042, 1.0)
    background.inputs["Strength"].default_value = 0.32

    add_area("Key | warm softbox", (-3.6, -3.8, 4.8), (0.0, 0.0, 0.85), 580.0, (1.0, 0.73, 0.48), 4.0)
    add_area("Fill | cool strip", (3.8, -1.6, 3.6), (0.0, 0.0, 1.0), 390.0, (0.48, 0.72, 1.0), 3.0, shape="RECTANGLE", size_y=1.2)
    add_area("Rim | amber edge", (0.2, 3.1, 4.1), (0.0, 0.0, 1.0), 720.0, (1.0, 0.39, 0.14), 2.3)
    add_area("Top | broad neutral", (-0.2, 0.1, 5.6), (0.0, 0.0, 0.6), 340.0, (0.80, 0.88, 1.0), 3.5)

    camera_data = bpy.data.cameras.new("P10 | 55mm product camera")
    camera = bpy.data.objects.new("P10 | Product Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (2.35, -4.95, 2.98)
    aim(camera, (0.0, -0.03, 1.02))
    camera_data.lens = 65.0
    camera_data.dof.use_dof = False
    scene.camera = camera
    return scene


def configure_render(scene, width=1500, height=1125):
    engine_ids = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "CYCLES" if "CYCLES" in engine_ids else "BLENDER_EEVEE"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.use_file_extension = False
    scene.render.filepath = os.path.join(SHOT_DIR, "06_final.png")
    scene.render.resolution_percentage = 100
    if scene.render.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = 16
        scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0


def render_to(scene, filepath, width, height):
    scene.render.filepath = filepath
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.use_file_extension = False
    if scene.render.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = 16
        scene.cycles.use_denoising = True
    bpy.ops.render.render(write_still=True)


def add_emission_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*color, 1.0)
    emission.inputs["Strength"].default_value = 0.8
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(emission.outputs[0], output.inputs["Surface"])
    return mat


def add_diagram_box(scene, name, text, location, dims, color, text_material):
    x, y, z = location
    w, h, depth = dims
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata([(x - w / 2, y - h / 2, z), (x + w / 2, y - h / 2, z), (x + w / 2, y + h / 2, z), (x - w / 2, y + h / 2, z)], [], [(0, 1, 2, 3)])
    mesh.update()
    box = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(box)
    box.data.materials.append(add_emission_material(name + " color", color))
    curve = bpy.data.curves.new(name + " label", type="FONT")
    curve.body = text
    curve.size = 0.15
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    label = bpy.data.objects.new(name + " label", curve)
    scene.collection.objects.link(label)
    label.location = (location[0], location[1], location[2] + depth * 0.55)
    curve.materials.append(text_material)
    return box


def make_node_flow_diagram(main_scene):
    scene = bpy.data.scenes.new("P10 | PBR node flow diagram")
    scene.render.engine = main_scene.render.engine
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    if scene.render.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = 4
        scene.cycles.use_denoising = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.use_file_extension = False
    scene.render.filepath = os.path.join(SHOT_DIR, "05_nodes.png")
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.world = bpy.data.worlds.new("P10 | diagram background")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.018, 0.030, 0.045, 1.0)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    white = add_emission_material("Diagram | ivory type", (0.82, 0.91, 0.96))
    muted = add_emission_material("Diagram | muted type", (0.45, 0.62, 0.70))

    bg_mat = add_emission_material("Diagram | background", (0.018, 0.030, 0.045))
    bg_mesh = bpy.data.meshes.new("PBR node diagram | background mesh")
    bg_mesh.from_pydata([(-4.3, -4.3, -0.10), (4.3, -4.3, -0.10), (4.3, 4.3, -0.10), (-4.3, 4.3, -0.10)], [], [(0, 1, 2, 3)])
    bg_mesh.update()
    bg_obj = bpy.data.objects.new("PBR node diagram | background", bg_mesh)
    scene.collection.objects.link(bg_obj)
    bg_obj.data.materials.append(bg_mat)

    title = bpy.data.curves.new("Diagram title", type="FONT")
    title.body = "KESTREL-09  |  UV + PBR MATERIAL FLOW"
    title.size = 0.24
    title.align_x = "CENTER"
    title_obj = bpy.data.objects.new("Diagram title", title)
    scene.collection.objects.link(title_obj)
    title_obj.location = (0.0, 2.78, 0.0)
    title.materials.append(white)

    def add_wires(wires):
        vertices = []
        faces = []
        half = 0.009
        for points in wires:
            for (x0, y0), (x1, y1) in zip(points, points[1:]):
                start = len(vertices)
                if abs(y1 - y0) < 1e-6:
                    vertices.extend([(x0, y0 - half, -0.025), (x1, y1 - half, -0.025), (x1, y1 + half, -0.025), (x0, y0 + half, -0.025)])
                else:
                    vertices.extend([(x0 - half, y0, -0.025), (x1 - half, y1, -0.025), (x1 + half, y1, -0.025), (x0 + half, y0, -0.025)])
                faces.append((start, start + 1, start + 2, start + 3))
        mesh = bpy.data.meshes.new("PBR node connections mesh")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new("PBR node connections", mesh)
        scene.collection.objects.link(obj)
        obj.data.materials.append(muted)

    input_rows = [
        (2.15, "BASE COLOR  /  sRGB", (0.72, 0.26, 0.08)),
        (1.42, "AMBIENT OCCLUSION  /  DATA", (0.24, 0.30, 0.33)),
        (0.69, "ROUGHNESS  /  DATA", (0.29, 0.37, 0.40)),
        (-0.04, "METALLIC  /  DATA", (0.47, 0.55, 0.58)),
        (-0.77, "NORMAL  /  NON-COLOR", (0.42, 0.31, 0.54)),
        (-2.15, "EMISSION  /  sRGB", (0.95, 0.34, 0.07)),
    ]
    for y, label, color in input_rows:
        add_diagram_box(scene, "Map | " + label, label, (-3.00, y, 0.0), (2.70, 0.46, 0.08), color, white)

    add_diagram_box(scene, "Base color and AO", "BASE COLOR\n× AMBIENT OCCLUSION", (-0.35, 1.72, 0.0), (1.55, 0.64, 0.08), (0.18, 0.32, 0.38), white)
    add_diagram_box(scene, "Normal Map node", "TANGENT\nNORMAL MAP", (-0.35, -1.34, 0.0), (1.55, 0.64, 0.08), (0.30, 0.22, 0.38), white)
    add_diagram_box(scene, "Principled BSDF", "PRINCIPLED\nBSDF", (2.05, 0.05, 0.0), (1.90, 4.90, 0.09), (0.13, 0.28, 0.33), white)
    add_diagram_box(scene, "Material Output", "MATERIAL\nOUTPUT", (4.05, 0.05, 0.0), (1.10, 0.80, 0.09), (0.22, 0.35, 0.31), white)
    add_wires([
        [(-1.65, 2.15), (-1.35, 2.15), (-1.35, 1.88), (-1.125, 1.88)],
        [(-1.65, 1.42), (-1.35, 1.42), (-1.35, 1.56), (-1.125, 1.56)],
        [(0.425, 1.72), (0.78, 1.72), (0.78, 1.50), (1.10, 1.50)],
        [(-1.65, 0.69), (1.10, 0.69)],
        [(-1.65, -0.04), (1.10, -0.04)],
        [(-1.65, -0.77), (-1.35, -0.77), (-1.35, -1.34), (-1.125, -1.34)],
        [(0.425, -1.34), (0.78, -1.34), (0.78, -1.42), (1.10, -1.42)],
        [(-1.65, -2.15), (0.78, -2.15), (0.78, -2.00), (1.10, -2.00)],
        [(3.00, 0.05), (3.50, 0.05)],
    ])

    camera_data = bpy.data.cameras.new("Diagram camera")
    camera = bpy.data.objects.new("Diagram camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.0, 0.0, 10.0)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 10.0
    scene.camera = camera
    bpy.ops.render.render(write_still=True, scene=scene.name)
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.scenes.remove(scene)


def main():
    if bpy.data.filepath and os.path.abspath(bpy.data.filepath) != os.path.abspath(P9_BLEND):
        bpy.ops.wm.open_mainfile(filepath=P9_BLEND)
    scene = bpy.context.scene
    scene.name = "P10 | Kestrel Workshop"
    for name in os.listdir(EXT_TEX):
        source = os.path.join(EXT_TEX, name)
        target = os.path.join(POLY_TEX_DIR, name)
        if os.path.isfile(source):
            shutil.copy2(source, target)

    # Remove the P9 studio shell and keep the modeled toolbox asset intact.
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"} or obj.name in {"Studio_Floor", "Blockout_Body_Proof"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    toolbox_objects = list(bpy.data.objects)

    for obj in toolbox_objects:
        if obj.type in {"MESH", "CURVE", "FONT"}:
            obj.location *= MODEL_SCALE
            obj.scale *= MODEL_SCALE
            apply_object_scale(obj)
    lower = object_bounds_z(toolbox_objects)
    raise_by = TABLE_TOP - lower
    for obj in toolbox_objects:
        if obj.type in {"MESH", "CURVE", "FONT"}:
            obj.location.x -= 0.55
            obj.location.z += raise_by

    # Import the external Poly Haven model from its original Blender asset.
    with bpy.data.libraries.load(EXT_BLEND, link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    lamp_objects = [obj for obj in data_to.objects if obj]
    for obj in lamp_objects:
        scene.collection.objects.link(obj)
        obj.location *= LAMP_SCALE
        obj.scale *= LAMP_SCALE
        apply_object_scale(obj)
    lamp_floor = object_bounds_z(lamp_objects)
    for obj in lamp_objects:
        obj.location.x += 0.55
        obj.location.y += 0.02
        obj.location.z += TABLE_TOP - lamp_floor

    # Give the original P9 palette accurate surface responses before adding the new maps.
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            continue
        if "Titanium" in material.name:
            bsdf.inputs["Metallic"].default_value = 0.82
            bsdf.inputs["Roughness"].default_value = 0.27
        elif "Carbon" in material.name:
            bsdf.inputs["Metallic"].default_value = 0.16
            bsdf.inputs["Roughness"].default_value = 0.61
        elif "Graphite" in material.name:
            bsdf.inputs["Metallic"].default_value = 0.48
            bsdf.inputs["Roughness"].default_value = 0.38
        else:
            bsdf.inputs["Roughness"].default_value = 0.43

    scene = create_stage()
    configure_render(scene, 900, 675)
    lamp_pbr = build_lamp_material()
    lamp_glass = simple_material("External | Lamp glass and filament", (0.30, 0.10, 0.025), metallic=0.05, roughness=0.14, emission=(1.0, 0.25, 0.035), emission_strength=1.5)
    for obj in lamp_objects:
        if "bulb" in obj.name.lower():
            set_object_material(obj, lamp_glass)
        else:
            set_object_material(obj, lamp_pbr)

    # First process image: the original P9 model and the external lamp before the toolbox PBR pass.
    render_to(scene, os.path.join(SHOT_DIR, "01_model.png"), 900, 675)

    # Hand-mark seams at open boundaries and hard transitions, then unwrap and pack.
    body = unwrap_all_meshes(toolbox_objects)
    custom_maps = make_toolbox_textures()
    own_pbr = build_toolbox_material(custom_maps)
    if body:
        set_object_material(body, own_pbr)

    # Distinct PBR material classes on the toolbox preserve painted, metal, rubber, and glass areas.
    metal_trim = simple_material("Kestrel | Brushed titanium", (0.28, 0.40, 0.44), metallic=0.84, roughness=0.28)
    dark_panel = simple_material("Kestrel | Graphite panel", (0.025, 0.050, 0.060), metallic=0.50, roughness=0.38)
    rubber = simple_material("Kestrel | Rubber feet", (0.012, 0.020, 0.024), metallic=0.0, roughness=0.72)
    display = simple_material("Kestrel | Glass display", (0.018, 0.11, 0.15), metallic=0.18, roughness=0.14, emission=(0.015, 0.22, 0.31), emission_strength=0.72)
    amber = simple_material("Kestrel | Safety amber", (0.92, 0.24, 0.035), metallic=0.18, roughness=0.34, emission=(0.85, 0.11, 0.012), emission_strength=0.45)
    trim_names = {"Front_Guards_Mirror", "Top_Rail_L", "Top_Rail_R", "Fastener_L_High", "Fastener_R_High", "Fastener_L_Low", "Fastener_R_Low", "Fastener_Core_L_High", "Fastener_Core_R_High", "Fastener_Core_L_Low", "Fastener_Core_R_Low"}
    panel_names = {"Front_Control_Panel", "Panel_Display_Bezel", "Panel_Label_Plate", "Side_Armor_L", "Side_Armor_R"}
    foot_names = {"Foot_L_B", "Foot_L_F", "Foot_R_B", "Foot_R_F", "Foot_Pad_L_B", "Foot_Pad_L_F", "Foot_Pad_R_B", "Foot_Pad_R_F", "Corner_Bumper_L", "Corner_Bumper_R"}
    for name in trim_names:
        obj = bpy.data.objects.get(name)
        if obj:
            set_object_material(obj, metal_trim)
    for name in panel_names:
        obj = bpy.data.objects.get(name)
        if obj:
            set_object_material(obj, dark_panel)
    for name in foot_names:
        obj = bpy.data.objects.get(name)
        if obj:
            set_object_material(obj, rubber)
    for name in {"Panel_Display_Glass", "Panel_Display_Scanline", "Panel_Status_Cyan"}:
        obj = bpy.data.objects.get(name)
        if obj:
            set_object_material(obj, display)
    obj = bpy.data.objects.get("Panel_Status_Amber")
    if obj:
        set_object_material(obj, amber)

    # Render a UV checker pass to make distortion and texel scale visible in the project documentation.
    checker = bpy.data.materials.new("UV review | Checker test")
    checker.use_nodes = True
    nodes = checker.node_tree.nodes
    links = checker.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-500, 0)
    checker_tex = nodes.new("ShaderNodeTexChecker")
    checker_tex.location = (-260, 0)
    checker_tex.inputs["Color1"].default_value = (0.015, 0.035, 0.045, 1.0)
    checker_tex.inputs["Color2"].default_value = (0.88, 0.51, 0.12, 1.0)
    checker_tex.inputs["Scale"].default_value = 12.0
    links.new(texcoord.outputs["UV"], checker_tex.inputs["Vector"])
    links.new(checker_tex.outputs["Color"], bsdf.inputs["Base Color"])
    if body:
        set_object_material(body, checker)
        # The source toolbox mesh has face material indices from its original palette.
        # Reset them for this single-slot checker pass so every polygon samples the UV map.
        for polygon in body.data.polygons:
            polygon.material_index = 0
        render_to(scene, os.path.join(SHOT_DIR, "04_checker.png"), 900, 675)
        set_object_material(body, own_pbr)

    # Render an educational map-to-shader diagram that matches the live node tree in the blend file.
    make_node_flow_diagram(scene)

    scene = bpy.data.scenes.get("P10 | Kestrel Workshop") or bpy.context.scene
    configure_render(scene, 1200, 900)
    scene.render.use_compositing = False
    render_to(scene, os.path.join(SHOT_DIR, "06_final.png"), 1200, 900)

    # Keep all image paths relative to this project and pack them into the blend for portability.
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath:
            absolute = os.path.abspath(image.filepath) if not image.filepath.startswith("//") else bpy.path.abspath(image.filepath)
            if not os.path.exists(absolute):
                for fallback in (os.path.join(ROOT, image.filepath.removeprefix("//")), os.path.join(EXT_TEX, os.path.basename(image.filepath)), os.path.join(TEX_DIR, os.path.basename(image.filepath))):
                    if os.path.exists(fallback):
                        absolute = fallback
                        break
            if os.path.exists(absolute):
                image.filepath = "//" + os.path.relpath(absolute, ROOT).replace("\\", "/")
    bpy.ops.file.pack_all()
    scene.render.filepath = "//screenshots/06_final.png"
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("P10_BUILD_COMPLETE", BLEND_OUT)
    print("SCENE_OBJECTS", len(bpy.data.objects), "MATERIALS", len(bpy.data.materials), "IMAGES", len(bpy.data.images))


if __name__ == "__main__":
    main()
