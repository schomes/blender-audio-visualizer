# Iterates through each object in a group named "Group" and animates each object with f-curve values from a sound file

import bpy
from random import randint

#####################################################
## Animation functions
####################################################

def animateActiveObject():

    # add a driver to modify properties with f-curves (from sound)
    fcurve = bpy.context.object.driver_add("location", 2) # z-axis location
    drv = fcurve.driver
    drv.type = 'SCRIPTED'
    drv.expression += ' + x * 10'
    drv.show_debug_info = True

    var = drv.variables.new()
    var.name = 'x'
    var.type = 'TRANSFORMS'

    targ = var.targets[0]
    targ.id = bpy.data.objects["Speaker"]
    targ.transform_type = 'LOC_X'

#####################################################
## Speaker functions
####################################################

def createSpeaker():
    # add speaker
    bpy.ops.object.speaker_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

def bakeSoundToSpeaker(name):

    # deselect all selected objects
    bpy.ops.object.select_all(action='DESELECT')

    # select speaker by name
    object = bpy.data.objects[name]
    object.select = True

    # add initial keyframes for location, rotation, and scale
    bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')

    # change to the Graph Editor
    bpy.context.area.type = 'GRAPH_EDITOR'

    # set lowest and highest frequencies
    lowest_freq = 0
    highest_freq = 100000

    # bake f-curves to speaker
    #bpy.ops.graph.sound_bake(filepath = '/Users/DavidSchommer/Music/Dewolfe.co.uk/Dubstep/GarethYoung/Unbreakable_DWCD_0540_trk_100.WAV', low = (lowest_freq), high = (highest_freq), attack = 0.005, release = 0.200, threshold = 0, sthreshold = 0.100)
    audioPath = bpy.context.scene.audio_path
    # convert to absolute path
    audioPathAbsolute = bpy.path.abspath(audioPath)
    bpy.ops.graph.sound_bake(filepath = audioPathAbsolute, low = (lowest_freq), high = (highest_freq), attack = 0.005, release = 0.200, threshold = 0, sthreshold = 0.100)


#####################################################
## Group functions
####################################################

def animateGroup(groupName):

    ##################
    ## set up scene ##
    ##################
    scn = bpy.context.scene

    # allows us to restore the original active object
    obActive = bpy.context.active_object
    obActiveIsSelected = obActive.select

    obj = bpy.context.object
    groupName = "Group"

    # deselect all selected objects
    bpy.ops.object.select_all(action='DESELECT')

    # attempt to find group_name, set this to the variable 'group'
    if groupName in bpy.data.groups:
        group = bpy.data.groups[groupName]

    print(group)

    for ob in group.objects:
        objectName = ob.name
        print(objectName)
        # set the active object to ob
        scn.objects.active = ob

        ob.select = True
        animateActiveObject()
        ob.select = False

    # restore active object to the original active object
    scn.objects.active = obActive
    obActive.select = obActiveIsSelected

    bpy.context.area.type = 'VIEW_3D'


#####################################################
## UI
####################################################

def initSceneProperties(scn):
    bpy.types.Scene.MyBool = bpy.props.BoolProperty(
        name = "Boolean", 
        description = "True or False?")
    scn['MyBool'] = True
    return

initSceneProperties(bpy.context.scene)

class AudioVisualizerPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Audio Visualizer Panel"
    bl_idname = "OBJECT_PT_avpanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Audio Visualizer"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Audio Visualizer", icon='SPEAKER')
        
        col = layout.column()
        col.prop(context.scene, 'audio_path')

        #animationOptions = bpy.props.EnumProperty(name = "animation_options", items=[('translate_x', 'translate by x', 'translate by x'), ('translate_y', 'translate by y', 'translate by y')])
        #row = layout.row()
        #row.prop(self, 'animation_options', expand=True)
        row = layout.row(align=True)
        row.prop(context.object, "hide_render",text="Render")
        row.prop(context.object, "hide",text="View")
        
        layout.prop(context.scene, 'MyBool')

        row = layout.row()
        row.operator("audiovisualizer.execute", text = "Run")
        
        


class SimpleOperator(bpy.types.Operator):
    """Generate animations from sound file"""
    bl_idname = "audiovisualizer.execute"
    bl_label = "Audio Visualize"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # set current frame to 0
        bpy.context.scene.frame_current = 0
        # Create speaker object (assumption: the speaker object is named 'Speaker')
        createSpeaker()
        # pass name of newly created speaker instead
        bakeSoundToSpeaker('Speaker')
        animateGroup('Group')
        return {'FINISHED'}

#####################################################
## Registration
####################################################

def register():
    bpy.utils.register_class(AudioVisualizerPanel)
    bpy.utils.register_class(SimpleOperator)
    # allows selecting path for audio file
    bpy.types.Scene.audio_path = bpy.props.StringProperty \
      (
      name = "Audio File",
      default = "",
      description = "Define the path of an audio file",
      subtype = 'FILE_PATH'
      )
      
def unregister():
    bpy.utils.unregister_class(AudioVisualizerPanel)
    bpy.utils.unregister_class(SimpleOperator)
    del bpy.types.Scene.audio_path

if __name__ == "__main__":
    register()
