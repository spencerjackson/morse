import sys

try:
    import GameLogic
except ImportError:
    import sys
    #TODO: the only reason why we need this GameLogic import is for the @service 
    # decorator that need somehow to know where to register the
    # service...
    print("services are only available within Blender")
    sys.exit(-1)

from functools import partial

from morse.core.exceptions import MorseServiceError

class MorseServices:
    def __init__(self, impls = []):
        """ Initializes the different MORSE request managers from a list
        of Python classes.

        :param list impls: a list of Python class names (strings) with their module
                path that implement the RequestManager interface.
        """
        self._request_managers = {}
        self._service_mappings = {}
    
        for impl in impls:
            self.add_request_manager(impl)

    def add_request_manager(self, impl):
        """ Initializes and adds a new request manager from
        its name.

        :param string impl: the name (and path) of the Python class that
                implements the RequestManager interface (eg: 'SocketRequestManager',
                'YarpRequestManager',...).
        """
        # Import the module containing the class
        modulename, classname = impl.rsplit('.', 1)
        try:
            __import__(modulename)
        except ImportError as detail:
            print ("ERROR: Request Manager %s not found." % detail)
            return
        module = sys.modules[modulename]

        if not module.__name__ in self._request_managers:
            # Create an instance of the object class
            try:
                klass = getattr(module, classname)
            except AttributeError as detail:
                print ("ERROR: Request manager  attribute not found: %s" % detail)
                return 
            instance = klass()

            self._request_managers[classname] = instance
            print("Successfully initialized the %s request manager." % classname)


    def register_request_manager_mapping(self,component, request_manager):
        """Adds a mapping between a component and a request manager: all
        services exposed by this component are handled by this request manager.

        A component may have 0, 1 or more request managers. if more than one,
        each request manager can independently invoke the service.
        
        :param string component: the name of the component that use *request_manager*
                as request manager.
        :param string request_manager: the name of the request manager (eg: 
                'SocketRequestManager', 'YarpRequestManager',...)
        
        """

        if not request_manager in self._request_managers:
            raise MorseServiceError("Request manager '%s' has not been registered!" % request_manager)

        instance = self._request_managers[request_manager]

        if component in self._service_mappings:
            self._service_mappings[component].append(instance)
        else:
            self._service_mappings[component] = [instance]


    def __del__(self):

        # Removes all registered request managers, calling their
        # destructors.
        self._request_managers.clear()

        self._service_mappings.clear()

    def get_request_managers(self, component):
        if not component in self._service_mappings:
           print("ERROR: no service manager is available for the " + component + " component! This error " +  \
                "can have several causes. Maybe you forgot to add the middleware 'empty', or " + \
                "you are using a middleware that does not currently support requests. ")
           raise MorseServiceError("No request manager has been mapped to the component %s" % component)
        
        return self._service_mappings[component]

    def process(self):
        """ Calls the *process()* method of each registered request manager.
        """
        for name, instance in self._request_managers.items():
            instance.process()


def do_service_registration(fn, component_name = None, service_name = None, request_managers = None):

    if not component_name:
        print("ERROR! A service has been registered without component: " + str(fn))
        return

    if not request_managers:
        request_managers = GameLogic.morse_services.get_request_managers(component_name)

    for manager in request_managers:
        name = service_name if service_name else fn.__name__
        print("Registering service " + name + " in " + component_name + " (using " + manager.__class__.__name__ + ")")
        manager.register_service(component_name, fn, name)

def service(fn = None, component = None, name = None):
    """ The '@service' decorator.

    This decorator can be used to automagically register a service in
    MORSE. Simply decorate the method you want to export as a RPC service
    with @service and MORSE automatically add and register it with the
    right middleware (depending on what is specified in the simulation
    configuration file).

    This decorator works both with free function and for methods in
    classes inheriting from MorseObjectClass. In the former case, you
    must specify a component (your service will belong to this
    namespace), in the later case, it is automatically set to the name
    of the corresponding MORSE component.

    :param callable fn: [automatically set by Python to point to the
    decorated function] 
    
    :param string component: you MUST set this parameter to define the
    name of the component which export the service ONLY for free
    functions. Cf explanation above.

    :param string name: by default, the name of the service is the name
    of the method. You can override it by setting the 'name' argument.

    """
    if hasattr(fn, "__call__"):
        # If the @service decorator has no explicit parameter, then Python
        # pass directly the function -> a callable. We can register it.
        if not component:
            # If component is not defined, we assume it is a class method.
            # In this case, the service registration is defered to the
            # class instanciation (cf object.py), and we simply mark
            # this method as a service.
            print("Method service "+ fn.__name__)
            fn._morse_service = True
            fn._morse_service_name = name
            return fn
        else:
            print("Free service "+ fn.__name__)
            # We assume it's a free function, and we register it.
            do_service_registration(fn, component, name, None)
            return fn
    else:
         # ...else, we build a new decorator
        return partial(service, component = component, name = name)
