Component bindings with middlewares (hooks) 
===========================================

Description of hooks 
--------------------

MORSE sensors and actuators are completely independent of any middleware,
and do not include themselves any means of passing the data they use.
To be able to use this data outside the simulator, it is necessary to bind
a middleware to every component, specifying the expected behavior.

When a component is linked to a middleware, a function described in the 
middleware will be added to the list of methods executed by the component, 
to be called each time the component executes its main task. In this way, 
the middleware can read the data provided by the component via a *hook*, 
which is an established data structure.

MORSE components have a property called ``modified_data``. It is a list 
that contains the data that can be exchanged with external programs. They 
also have a dictionary called ``local_data`` that has the names of the 
variables as well as their values, and is reserved for internal use in the 
component. Middlewares create the "hooks" to ``modified_data`` only.

Data modifiers can also be applied to the ``modified_data`` array, to produce 
data that is more realistic. In the case of sensors, the modifiers are 
applied before the data is sent through the middleware. The opposite happens 
with actuators, which read data through middlewares and then change it using 
modifiers, before using it inside of Blender.

Configuration 
-------------

This binding is currently done via a Python file called ``component_config.py``
which must be internal to the Blender scenario file. The configuration file 
should be edited from a **Text Editor** window in Blender.
It consists of two dictionaries indexed by the name of the components:

- ``component_mw``: Lists which middlewares are bound to the specific 
  component. The value of the dictionary is a list. The first element of the 
  list is the name of the Middleware, and must be written exactly as the 
  name of the Empty object that represents the Middleware in the scene.

  In the case of Yarp and Text, the second item will be the name of the 
  function to be added to the component's action list For Pocolibs, the second 
  item is the type of poster, and the third is the name of the poster.

- ``component_modifier``: Lists the modifiers affecting each of the components. 
  The value of the dictionary is a list, where each element is itself a list 
  representing a modifier. Each modifier list has two elements: the name of 
  the modifier and the name of the function to use.

Example::

  component_mw = {
   	Gyroscope": ["Yarp", "post_message"],
    "Motion_Controller": ["Yarp", "read_message"],
    "Motion_Controller.001": ["Pocolibs", "genPos", "p3dSpeedRef"],
    "CameraMain": ["Yarp", "post_image_RGBA"]
  }
  
  component_modifier = {
    "GPS.001": [ ["NED", "blender_to_ned"], ["Json", "json_encode"] ],
    "Motion_Controller": [ ["NED", "ned_to_blender"] ]
  }

