import Live
from typing import Tuple, Any, Optional, Callable
from .handler import AbletonOSCHandler

class DeviceHandler(AbletonOSCHandler):
    def __init__(self, manager):
        super().__init__(manager)
        self.class_identifier = "device"

    def _set_mixer_property(self, target, prop, params: Tuple) -> None:
        if prop == 'sends':
            send_id, value = params
            parameter_object = getattr(target.mixer_device, prop)[send_id]
            self.logger.info("Setting property for %s: %s (new value %s)" % (self.class_identifier, prop, params[0]))
            parameter_object.value = value
        else:
            parameter_object = getattr(target.mixer_device, prop)
            self.logger.info("Setting property for %s: %s (new value %s)" % (self.class_identifier, prop, params[0]))
            parameter_object.value = params[0]

    def _get_mixer_property(self, target, prop, params: Optional[Tuple] = ()) -> Tuple[Any]:
        if prop == 'sends':
            send_id, = params
            parameter_object = getattr(target.mixer_device, prop)[send_id]
            self.logger.info("Getting property for %s: %s = %s" % (self.class_identifier, prop, parameter_object.value))
            return send_id, parameter_object.value,
        else:
            parameter_object = getattr(target.mixer_device, prop)
            self.logger.info("Getting property for %s: %s = %s" % (self.class_identifier, prop, parameter_object.value))
            return parameter_object.value,

    def _start_mixer_listen(self, target, prop, params: Optional[Tuple] = ()) -> None:
        if prop == 'sends':
            track_id = -1 
            send_id = -1
            if len(params) == 2:
                track_id, send_id, = params
            if len(params) == 6:
                track_id, send_id, = params[4:]
            parameter_object = getattr(target.mixer_device, prop)[send_id]
        else:
            parameter_object = getattr(target.mixer_device, prop)

        def property_changed_callback():
            value = parameter_object.value
            self.logger.info("Property %s changed of %s %s: %s" % (prop, self.class_identifier, str(params), value))
            osc_address = "/live/%s/get/%s" % (self.class_identifier, prop)
            self.osc_server.send(osc_address, (*params, value,))

        listener_key = (prop, tuple(params))
        if listener_key in self.listener_functions:
            self.logger.info("Already assigned listener for %s %s, property: %s" % (self.class_identifier, str(params), prop))
        else:
            self.logger.info("Adding listener for %s %s, property: %s" % (self.class_identifier, str(params), prop))
            parameter_object.add_value_listener(property_changed_callback)
            self.listener_functions[listener_key] = property_changed_callback
        #--------------------------------------------------------------------------------
        # Immediately send the current value
        #--------------------------------------------------------------------------------
        property_changed_callback()

    def _stop_mixer_listen(self, target, prop, params: Optional[Tuple[Any]] = ()) -> None:
        if prop == 'sends':
            track_id, send_id, = params
            parameter_object = getattr(target.mixer_device, prop)[send_id]
        else:
            parameter_object = getattr(target.mixer_device, prop)

        listener_key = (prop, tuple(params))
        if listener_key in self.listener_functions:
            self.logger.info("Removing listener for %s %s, property %s" % (self.class_identifier, str(params), prop))
            listener_function = self.listener_functions[listener_key]
            parameter_object.remove_value_listener(listener_function)
            del self.listener_functions[listener_key]
        else:
            self.logger.warning("No listener function found for property: %s (%s)" % (prop, str(params)))

    def init_api(self):
        def create_device_callback(func, *args, include_ids: bool = False):
            def device_callback(params: Tuple[Any]):
                track_index, device_index = int(params[0]), int(params[1])
                device = self.song.tracks[track_index].devices[device_index]
                rack_device = device if isinstance(device, Live.RackDevice.RackDevice) else None
                if rack_device is not None:
                    device = rack_device
                if (include_ids):
                    rv = func(device, *args, params[0:])
                else:
                    rv = func(device, *args, params[2:])

                if rv is not None:
                    return (track_index, device_index, *rv)

            return device_callback

        def create_chain_callback(func: Callable,
                                  *args,
                                  include_chain_id: bool = False):
            def chain_callback(params: Tuple[Any]):
                track_index, device_index, chain_index = int(params[0]), int(params[1]), int(params[2])
                device = self.song.tracks[track_index].devices[device_index]
                rack_device = device if isinstance(device, Live.RackDevice.RackDevice) else None
                if rack_device is not None and len(rack_device.chains):
                    chain = self.song.tracks[track_index].devices[device_index].chains[chain_index]
                    if (include_chain_id):
                        rv = func(chain, *args, params[0:])
                    else:
                        rv = func(chain, *args, params[2:])

                    if rv is not None:
                        return (track_index, device_index, chain_index, *rv)
            return chain_callback
        
        def create_chain_device_callback(func: Callable,
                                  *args,
                                  include_chain_id: bool = False):
            def chain_device_callback(params: Tuple[Any]):
                track_index, device_index, chain_index, sub_device_index, chain_subdevice_chain_index, send_index = int(params[0]), int(params[1]), int(params[2]), int(params[3]), int(params[4]), int(params[5])
                device = self.song.tracks[track_index].devices[device_index]
                rack_device = device if isinstance(device, Live.RackDevice.RackDevice) else None
                if rack_device is not None and len(rack_device.chains):
                    chain = rack_device.chains[chain_index]
                    chain_sub_device = chain.devices[sub_device_index] if isinstance(chain.devices[sub_device_index], Live.RackDevice.RackDevice) else None
                    if chain_sub_device is not None:
                        chain_sub_device_chain = chain_sub_device.chains[chain_subdevice_chain_index]
                        self.logger.info("we have sub device named %s" % chain_sub_device_chain.name )
                        if (include_chain_id):
                            rv = func(chain_sub_device_chain, *args, params)
                        else:
                            rv = func(chain_sub_device_chain, *args, params[6:])

                        if rv is not None:
                            return (track_index, device_index, chain_index, sub_device_index, send_index, *rv)
            return chain_device_callback

        methods = [
        ]
        properties_r = [
            "class_name",
            "name",
            "type"
        ]
        properties_rw = [
        ]

        for method in methods:
            self.osc_server.add_handler("/live/device/%s" % method,
                                        create_device_callback(self._call_method, method))

        for prop in properties_r + properties_rw:
            self.osc_server.add_handler("/live/device/get/%s" % prop,
                                        create_device_callback(self._get_property, prop))
            self.osc_server.add_handler("/live/device/start_listen/%s" % prop,
                                        create_device_callback(self._start_listen, prop))
            self.osc_server.add_handler("/live/device/stop_listen/%s" % prop,
                                        create_device_callback(self._stop_listen, prop))
        for prop in properties_rw:
            self.osc_server.add_handler("/live/device/set/%s" % prop,
                                        create_device_callback(self._set_property, prop))

        #--------------------------------------------------------------------------------
        # Device: Get/set parameter lists
        #--------------------------------------------------------------------------------
        def device_get_num_parameters(device, params: Tuple[Any] = ()):
            return len(device.parameters),

        def device_get_parameters_name(device, params: Tuple[Any] = ()):
            return tuple(parameter.name for parameter in device.parameters)

        def device_get_parameters_value(device, params: Tuple[Any] = ()):
            return tuple(parameter.value for parameter in device.parameters)

        def device_get_parameters_min(device, params: Tuple[Any] = ()):
            return tuple(parameter.min for parameter in device.parameters)

        def device_get_parameters_max(device, params: Tuple[Any] = ()):
            return tuple(parameter.max for parameter in device.parameters)

        def device_get_parameters_is_quantized(device, params: Tuple[Any] = ()):
            return tuple(parameter.is_quantized for parameter in device.parameters)

        def device_set_parameters_value(device, params: Tuple[Any] = ()):
            for index, value in enumerate(params):
                device.parameters[index].value = value


        def rack_get_chains_name(device, params: Tuple[Any] = ()):
            return tuple(chain.name for chain in device.chains)
        
        self.osc_server.add_handler("/live/device/get/num_parameters", create_device_callback(device_get_num_parameters))
        self.osc_server.add_handler("/live/device/get/parameters/name", create_device_callback(device_get_parameters_name))
        self.osc_server.add_handler("/live/device/get/parameters/value", create_device_callback(device_get_parameters_value))
        self.osc_server.add_handler("/live/device/get/parameters/min", create_device_callback(device_get_parameters_min))
        self.osc_server.add_handler("/live/device/get/parameters/max", create_device_callback(device_get_parameters_max))
        self.osc_server.add_handler("/live/device/get/parameters/is_quantized", create_device_callback(device_get_parameters_is_quantized))
        self.osc_server.add_handler("/live/device/set/parameters/value", create_device_callback(device_set_parameters_value))
        self.osc_server.add_handler("/live/rack/get/chains/name", create_device_callback(rack_get_chains_name))
        #--------------------------------------------------------------------------------
        # Device: Get/set individual parameters
        #--------------------------------------------------------------------------------
        def device_get_parameter_value(device, params: Tuple[Any] = ()):
            # Cast to ints so that we can tolerate floats from interfaces such as TouchOSC
            # that send floats by default.
            # https://github.com/ideoforms/AbletonOSC/issues/33
            param_index = int(params[0])
            return param_index, device.parameters[param_index].value
        
        # Uses str_for_value method to return the UI-friendly version of a parameter value (ex: "2500 Hz")
        def device_get_parameter_value_string(device, params: Tuple[Any] = ()):
            param_index = int(params[0])
            return param_index, device.parameters[param_index].str_for_value(device.parameters[param_index].value)
        
        def device_get_parameter_value_listener(device, params: Tuple[Any] = ()):

            def property_changed_callback():
                value = device.parameters[params[2]].value
                self.logger.info("Property %s changed of %s %s: %s" % ('value', 'device parameter', str(params), value))
                self.osc_server.send("/live/device/get/parameter/value", (*params, value,))

                value_string = device.parameters[params[2]].str_for_value(device.parameters[params[2]].value)
                self.logger.info("Property %s changed of %s %s: %s" % ('value_string', 'device parameter', str(params), value_string))
                self.osc_server.send("/live/device/get/parameter/value_string", (*params, value_string,))

            listener_key = ('device_parameter_value', tuple(params))
            if listener_key in self.listener_functions:
               device_get_parameter_remove_value_listener(device, params)

            self.logger.info("Adding listener for %s %s, property: %s" % ('device parameter', str(params), 'value'))
            device.parameters[params[2]].add_value_listener(property_changed_callback)
            self.listener_functions[listener_key] = property_changed_callback

            property_changed_callback()

        def device_get_parameter_remove_value_listener(device, params: Tuple[Any] = ()):
            listener_key = ('device_parameter_value', tuple(params))
            if listener_key in self.listener_functions:
                self.logger.info("Removing listener for %s %s, property %s" % (self.class_identifier, str(params), 'value'))
                listener_function = self.listener_functions[listener_key]
                device.parameters[params[2]].remove_value_listener(listener_function)
                del self.listener_functions[listener_key]
            else:
                self.logger.warning("No listener function found for property: %s (%s)" % (prop, str(params)))

        def device_set_parameter_value(device, params: Tuple[Any] = ()):
            param_index, param_value = params[:2]
            param_index = int(param_index)
            device.parameters[param_index].value = param_value

        def device_get_parameter_name(device, params: Tuple[Any] = ()):
            param_index = int(params[0])
            return param_index, device.parameters[param_index].name

        def device_is_rack(device, _):
            rack_device = device if isinstance(device, Live.RackDevice.RackDevice) else None
            if rack_device is not None:
                return True
            return False

        self.osc_server.add_handler("/live/device/get/parameter/value", create_device_callback(device_get_parameter_value))
        self.osc_server.add_handler("/live/device/get/parameter/value_string", create_device_callback(device_get_parameter_value_string))
        self.osc_server.add_handler("/live/device/set/parameter/value", create_device_callback(device_set_parameter_value))
        self.osc_server.add_handler("/live/device/get/parameter/name", create_device_callback(device_get_parameter_name))
        self.osc_server.add_handler("/live/device/get/device_is_rack", create_device_callback(device_is_rack))
        self.osc_server.add_handler("/live/device/start_listen/parameter/value", create_device_callback(device_get_parameter_value_listener, include_ids = True))
        self.osc_server.add_handler("/live/device/stop_listen/parameter/value", create_device_callback(device_get_parameter_remove_value_listener, include_ids = True))


        #--------------------------------------------------------------------------------
        # Volume, panning and send are properties of the chains's mixer_device so
        # can't be formulated as normal callbacks that reference properties of chain.
        #--------------------------------------------------------------------------------
        mixer_properties_rw = ["volume", "panning"]
        for prop in mixer_properties_rw:
            self.osc_server.add_handler("/live/chain/get/%s" % prop,
                                        create_chain_callback(self._get_mixer_property, prop))
            self.osc_server.add_handler("/live/chain/set/%s" % prop,
                                        create_chain_callback(self._set_mixer_property, prop))
            self.osc_server.add_handler("/live/chain/start_listen/%s" % prop,
                                        create_chain_callback(self._start_mixer_listen, prop, include_chain_id=True))
            self.osc_server.add_handler("/live/chain/stop_listen/%s" % prop,
                                        create_chain_callback(self._stop_mixer_listen, prop, include_chain_id=True))
            
        mixer_sends_properties_rw = "sends"
        self.osc_server.add_handler("/live/chain/get/%s" % mixer_sends_properties_rw,
                                    create_chain_device_callback(self._get_mixer_property, mixer_sends_properties_rw))
        self.osc_server.add_handler("/live/chain/set/%s" % mixer_sends_properties_rw,
                                    create_chain_device_callback(self._set_mixer_property, mixer_sends_properties_rw))
        self.osc_server.add_handler("/live/chain/start_listen/%s" % mixer_sends_properties_rw,
                                    create_chain_device_callback(self._start_mixer_listen, mixer_sends_properties_rw, include_chain_id=True))
        self.osc_server.add_handler("/live/chain/stop_listen/%s" % mixer_sends_properties_rw,
                                    create_chain_device_callback(self._stop_mixer_listen, mixer_sends_properties_rw, include_chain_id=True))

        
            
        #--------------------------------------------------------------------------------
        # Chain: Get/set parameter lists
        #--------------------------------------------------------------------------------

        # def device_get_num_parameters(device, params: Tuple[Any] = ()):
        #     return len(device.parameters),

        # def device_get_parameters_name(device, params: Tuple[Any] = ()):
        #     return tuple(parameter.name for parameter in device.parameters)

        # def device_get_parameters_value(device, params: Tuple[Any] = ()):
        #     return tuple(parameter.value for parameter in device.parameters)

        # def device_get_parameters_min(device, params: Tuple[Any] = ()):
        #     return tuple(parameter.min for parameter in device.parameters)

        # def device_get_parameters_max(device, params: Tuple[Any] = ()):
        #     return tuple(parameter.max for parameter in device.parameters)

        # def device_get_parameters_is_quantized(device, params: Tuple[Any] = ()):
        #     return tuple(parameter.is_quantized for parameter in device.parameters)

        # def device_set_parameters_value(device, params: Tuple[Any] = ()):
        #     for index, value in enumerate(params):
        #         device.parameters[index].value = value

        # self.osc_server.add_handler("/live/device/get/parameters/name", create_device_callback(device_get_parameters_name))
        # self.osc_server.add_handler("/live/device/get/parameters/value", create_device_callback(device_get_parameters_value))
        # self.osc_server.add_handler("/live/device/get/parameters/min", create_device_callback(device_get_parameters_min))
        # self.osc_server.add_handler("/live/device/get/parameters/max", create_device_callback(device_get_parameters_max))
        # self.osc_server.add_handler("/live/device/get/parameters/is_quantized", create_device_callback(device_get_parameters_is_quantized))
        # self.osc_server.add_handler("/live/device/set/parameters/value", create_device_callback(device_set_parameters_value))

        #--------------------------------------------------------------------------------
        # Chain: Get/set individual parameters
        #--------------------------------------------------------------------------------

        # def device_get_parameter_value(device, params: Tuple[Any] = ()):
        #     # Cast to ints so that we can tolerate floats from interfaces such as TouchOSC
        #     # that send floats by default.
        #     # https://github.com/ideoforms/AbletonOSC/issues/33
        #     param_index = int(params[0])
        #     return param_index, device.parameters[param_index].value
        
        # # Uses str_for_value method to return the UI-friendly version of a parameter value (ex: "2500 Hz")
        # def device_get_parameter_value_string(device, params: Tuple[Any] = ()):
        #     param_index = int(params[0])
        #     return param_index, device.parameters[param_index].str_for_value(device.parameters[param_index].value)
        
        # def device_get_parameter_value_listener(device, params: Tuple[Any] = ()):

        #     def property_changed_callback():
        #         value = device.parameters[params[2]].value
        #         self.logger.info("Property %s changed of %s %s: %s" % ('value', 'device parameter', str(params), value))
        #         self.osc_server.send("/live/device/get/parameter/value", (*params, value,))

        #         value_string = device.parameters[params[2]].str_for_value(device.parameters[params[2]].value)
        #         self.logger.info("Property %s changed of %s %s: %s" % ('value_string', 'device parameter', str(params), value_string))
        #         self.osc_server.send("/live/device/get/parameter/value_string", (*params, value_string,))

        #     listener_key = ('device_parameter_value', tuple(params))
        #     if listener_key in self.listener_functions:
        #        device_get_parameter_remove_value_listener(device, params)

        #     self.logger.info("Adding listener for %s %s, property: %s" % ('device parameter', str(params), 'value'))
        #     device.parameters[params[2]].add_value_listener(property_changed_callback)
        #     self.listener_functions[listener_key] = property_changed_callback

        #     property_changed_callback()

        # def device_get_parameter_remove_value_listener(device, params: Tuple[Any] = ()):
        #     listener_key = ('device_parameter_value', tuple(params))
        #     if listener_key in self.listener_functions:
        #         self.logger.info("Removing listener for %s %s, property %s" % (self.class_identifier, str(params), 'value'))
        #         listener_function = self.listener_functions[listener_key]
        #         device.parameters[params[2]].remove_value_listener(listener_function)
        #         del self.listener_functions[listener_key]
        #     else:
        #         self.logger.warning("No listener function found for property: %s (%s)" % (prop, str(params)))

        # def device_set_parameter_value(device, params: Tuple[Any] = ()):
        #     param_index, param_value = params[:2]
        #     param_index = int(param_index)
        #     device.parameters[param_index].value = param_value

        # def device_get_parameter_name(device, params: Tuple[Any] = ()):
        #     param_index = int(params[0])
        #     return param_index, device.parameters[param_index].name

        # self.osc_server.add_handler("/live/device/get/parameter/value_string", create_device_callback(device_get_parameter_value_string))
        # self.osc_server.add_handler("/live/device/set/parameter/value", create_device_callback(device_set_parameter_value))
        # self.osc_server.add_handler("/live/device/get/parameter/name", create_device_callback(device_get_parameter_name))
        # self.osc_server.add_handler("/live/device/stop_listen/parameter/value", create_device_callback(device_get_parameter_remove_value_listener, include_ids = True))