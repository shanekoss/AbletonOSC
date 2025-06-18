from ableton.v2.control_surface import ControlSurface # type: ignore
from ableton.v2.control_surface.elements import SliderElement, ButtonElement, EncoderElement # type: ignore
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_PB_TYPE, MIDI_NOTE_TYPE # type: ignore

from . import abletonosc
from .track_processor import TrackProcessor
from .preset_manager import PresetManager
from .abletonosc.constants import CC_LISTENERS, NOTE_LISTENERS, Channel_1_CC, Channel_1_Note, LOOP_VELOCITY, LOOP_FADE_STATES, LOOP_FADE_STATE, FADE_AMOUNT, FADER_ZERO, STATE, MIDI_ECHO
import importlib
import traceback
import logging
import math
import os
import Live # type: ignore

logger = logging.getLogger("abletonosc")

#TODO: refactor this file into multiple files - way too big
class Manager(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._c_instance = c_instance
        self.log_level = "info"

        # MIDI Handling Setup
        #TODO: CLEAR THESE HANDLERS ON DISCONNECT
        self._cc_listeners = []
        self._note_listeners = []
        self._sysex_listeners = []

        self.bankATempoIndex = -1
        self.state_index = -1
        self.currentBankAIndex = -1
        self.currentBankBIndex = -1
        self.tide_a_index = -1
        self.tide_pgm_index = -1
        self.portal_index = -1
        self.movement_y_index = -1
        self.movement_x_index = -1
        self.movement_wet_dry_index = -1
        self.portal_1_index = -1
        self.portal_2_index = -1
        self.portal_reverse_index = -1
        self.portal_wet_dry_index = -1
        self.portal_name_index = -1

        self.loopFadeStates = LOOP_FADE_STATES
        self.fadeLoops = False
        self.fadeSpeed = 0.01
        try:
            self.osc_server = abletonosc.OSCServer()
            self.schedule_message(0, self.tick)
            self.start_logging()
            self.init_api()
            self._setup_midi_handling()

            logger.info("AbletonOSC: Listening for OSC on port %d" % abletonosc.OSC_LISTEN_PORT)
        except OSError as msg:
            logger.error("Couldn't bind to port %d (%s)" % (abletonosc.OSC_LISTEN_PORT, msg))

        self.preset_mananger = PresetManager(c_instance)
        self.preset_mananger.logger = logger
        self.preset_mananger.manager = self
        self.preset_mananger.initialize_presets_file()
        self.track_processor = TrackProcessor()
        self.track_processor.manager = self
        self.track_processor.logger = logger
        self.track_processor.processTracks(self.song.tracks)
        self.track_processor.processReturnTracks(self.song.return_tracks)
        self.schedule_message(1, self.track_processor.get_portal_presets)
             
    def handle_volume_cc(self, value):
        logger.info(f"Volume CC changed to {value}")

    def _setup_midi_handling(self):
        """Initialize MIDI handling components"""
        # Enable receiving all MIDI messages
        self._c_instance.set_feedback_channels(list(range(16)))
        with self.component_guard():
            logger.info("Create listeners for all MIDI CC messages")
            for cc_type in CC_LISTENERS:
                self.register_cc_listener(cc_type[1], cc_type[0])
            for note_type in NOTE_LISTENERS:
                self.register_note_listener(note_type[1], note_type[0])

    def receive_midi(self, midi_bytes):
        logger.info(midi_bytes)
        """Process incoming MIDI messages"""
        if not midi_bytes:
            return

        try:
            status_byte = midi_bytes[0] & 0xF0  # Mask channel bits
            
            # MIDI CC Message (Control Change)
            if status_byte == 0xB0:
                channel = midi_bytes[0] & 0x0F
                cc_number = midi_bytes[1]
                value = midi_bytes[2]
                logger.debug(f"MIDI CC: ch{channel+1} cc{cc_number} val{value}")
                self._handle_cc(channel, cc_number, value)
            
            # MIDI Note Messages
            elif status_byte in (0x90, 0x80):
                channel = midi_bytes[0] & 0x0F
                note_number = midi_bytes[1]
                velocity = midi_bytes[2]
                is_note_on = status_byte == 0x90 and velocity > 0
                logger.debug(f"MIDI Note: ch{channel+1} note{note_number} vel{velocity}")
                self._handle_note(channel, note_number, is_note_on, velocity)
            
            # MIDI SYSEX Messages
            elif midi_bytes[0] == 0xF0 and midi_bytes[-1] == 0xF7:
                logger.debug("MIDI SYSEX received")
                self._handle_sysex(midi_bytes[1:-1])
            
            else:
                # Let Live handle other messages
                super(Manager, self).receive_midi(midi_bytes)
                
        except Exception as e:
            logger.error(f"MIDI processing error: {str(e)}")

    def _handle_cc(self, value, sender):
        channel = sender.message_channel()
        cc_num = sender.message_identifier()
        self.processCCMessage(channel, cc_num, value)

        # test_sysex = bytes([cc_num, value])
        # self.send_sysex(test_sysex)

    def _handle_note(self, channel, note_number, velocity):
        self.processNoteMessage(channel, note_number, velocity)

    def _handle_sysex(self, data):
        logger.info("SYSEX RECEIVED!!!")
        logger.info(data)
        """Process incoming SYSEX messages"""
        for callback in self._sysex_listeners:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"SYSEX callback error: {str(e)}")

    # MIDI Registration Methods
    def register_cc_listener(self, channel, cc_number):
        """Create and configure a single CC listener"""
        cc = SliderElement(MIDI_CC_TYPE, channel, cc_number)
        cc.add_value_listener(
            lambda value, sender=cc: self._handle_cc(value, sender),
            identify_sender=True
        )
        self._cc_listeners.append(cc)

    def register_note_listener(self, channel, note_number):
        """Create and configure a single Note listener"""
        nl = ButtonElement(True, MIDI_NOTE_TYPE, channel, note_number)
        # Fixed: Now properly captures sender reference in the lambda
        nl.add_value_listener(
            lambda value: self._handle_note(channel, note_number, value),
        )
        self._note_listeners.append(nl)

    def register_sysex_listener(self, callback):
        logger.info("Register callback for SYSEX messages")

    def send_midi_cc(self, channel, cc_num, value):
        """Send a MIDI CC message"""
        # Correct way to send MIDI in Ableton scripts
        self._send_midi(tuple([0xB0 | (channel & 0x0F), cc_num & 0x7F, value & 0x7F]))

    def send_midi_note(self, channel, note, velocity):
        """Send a MIDI Note message"""
        self._send_midi(tuple([0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F]))

    def send_sysex(self, sysex_bytes):
        masked_data = [byte & 0x7F for byte in sysex_bytes] 
        self._send_midi((0xF0, *masked_data, 0xF7))

    # Original Manager methods remain unchanged below this point
    def start_logging(self):
        """
        Start logging to a local logfile (logs/abletonosc.log),
        and relay error messages via OSC.
        """
        module_path = os.path.dirname(os.path.realpath(__file__))
        log_dir = os.path.join(module_path, "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir, 0o755)
        log_path = os.path.join(log_dir, "abletonosc.log")
        self.log_file_handler = logging.FileHandler(log_path)
        self.log_file_handler.setLevel(self.log_level.upper())
        formatter = logging.Formatter('(%(asctime)s) [%(levelname)s] %(message)s')
        self.log_file_handler.setFormatter(formatter)
        logger.addHandler(self.log_file_handler)

        class LiveOSCErrorLogHandler(logging.StreamHandler):
            def emit(handler, record):
                message = record.getMessage()
                message = message[message.index(":") + 2:]
                try:
                    self.osc_server.send("/live/error", (message,))
                except OSError:
                    # If the connection is dead, silently ignore errors
                    pass
        self.live_osc_error_handler = LiveOSCErrorLogHandler()
        self.live_osc_error_handler.setLevel(logging.ERROR)
        logger.addHandler(self.live_osc_error_handler)

    def stop_logging(self):
        logger.removeHandler(self.log_file_handler)
        logger.removeHandler(self.live_osc_error_handler)

    def init_api(self):
        def test_callback(params):
            logger.info("Received OSC OK")
            self.osc_server.send("/live/test", ("ok",))
        def reload_callback(params):
            self.reload_imports()
        def get_log_level_callback(params):
            return (self.log_level,)
        def set_log_level_callback(params):
            log_level = params[0]
            assert log_level in ("debug", "info", "warning", "error", "critical")
            self.log_level = log_level
            self.log_file_handler.setLevel(self.log_level.upper())

        self.osc_server.add_handler("/live/test", test_callback)
        self.osc_server.add_handler("/live/api/reload", reload_callback)
        self.osc_server.add_handler("/live/api/get/log_level", get_log_level_callback)
        self.osc_server.add_handler("/live/api/set/log_level", set_log_level_callback)

        with self.component_guard():
            self.handlers = [
                abletonosc.SongHandler(self),
                abletonosc.ApplicationHandler(self),
                abletonosc.ClipHandler(self),
                abletonosc.ClipSlotHandler(self),
                abletonosc.DeviceHandler(self),
                abletonosc.TrackHandler(self),
                abletonosc.ViewHandler(self),
                abletonosc.SceneHandler(self)
            ]

    # TODO: move these process functions to another file!
    def processCCMessage(self, channel, cc_num, value):
        handled = False
        if channel == 0:
            if cc_num == Channel_1_CC.BANK_A_SELECT:
                handled = True
                self.track_processor.setBankALoops(value)
            elif cc_num == Channel_1_CC.BANK_B_SELECT:
                handled = True
                self.track_processor.setBankBLoops(value)
            elif cc_num == Channel_1_CC.LOAD_PRESET:
                handled = True
                self.preset_mananger.load_preset_into_set(value)
            elif cc_num == Channel_1_CC.SAVE_PRESET:
                handled = True
                self.preset_mananger.save_current_set_as_preset(value)
            elif cc_num == Channel_1_CC.LOOP_FADE:
                handled = True
                self.fadeLoops = False if value < 127 else True
                if self.fadeLoops == False:
                    self.fade_timer.stop()
            elif cc_num == Channel_1_CC.LOOP_FADE_SPEED:
                self.fadeSpeed =  max(0.01, min(1 - (value / 127.0), 1.0))   
                handled = True

        if handled == False:
            logger.info(f"Unhandled CC CH{channel:02d} #{cc_num:03d} = {value:03d}")
    
    def processNoteMessage(self, channel, note, velocity):
        handled = False
        if channel == 0:
            if Channel_1_Note.LOOP1 <= note <= Channel_1_Note.LOOP16:
                if velocity == LOOP_VELOCITY.STOP_LOOP:
                    handled = True
                    self.stop_loop(note)
                elif velocity == LOOP_VELOCITY.START_LOOP:
                    handled = True
                    self.start_loop(note)
            elif note == MIDI_ECHO:
                handled = True
                self.send_midi_note(0, 127, 1)
        if handled == False:
            logger.info(f"Unhandled Note CH{channel:02d} #{note:03d} = {velocity:03d}")
    
    def start_loop(self, note):
        is_bank_a = note < Channel_1_Note.LOOP9
        clip_slot_index = self.currentBankAIndex if is_bank_a else self.currentBankBIndex
        track_index = self.track_processor.loop_tracks[note]
        if is_bank_a == False:
            #offset for bank b
            track_index + track_index + 1
        loop_state_name = f'LOOP{note + 1}'
        if self.song.tracks[track_index].clip_slots[clip_slot_index].has_clip:
            if self.fadeLoops:
                if math.isclose(self.song.tracks[track_index].mixer_device.volume.value, FADER_ZERO, rel_tol=1e-3):
                    self.song.tracks[track_index].mixer_device.volume.value = 0
                self.loopFadeStates[loop_state_name]['state'] = LOOP_FADE_STATE.FADING_IN
                self.fadeLoop({"track_index": track_index, "loop_state_name": loop_state_name})
            else:
                self.song.tracks[track_index].mixer_device.volume.value = FADER_ZERO
            self.song.tracks[track_index].clip_slots[clip_slot_index].clip.fire()
        else:
            logger.warning(f"Clip slot {clip_slot_index} for Loop{note+1} has no clip!")

    def fadeLoop(self, data):
        track_index = data['track_index']
        loop_state_name = data['loop_state_name']
        current_volume = self.song.tracks[track_index].mixer_device.volume.value
        if self.loopFadeStates[loop_state_name]['state'] == LOOP_FADE_STATE.FADING_IN:
            current_volume = current_volume + self.fadeSpeed * FADE_AMOUNT
            if current_volume > FADER_ZERO:
                current_volume = FADER_ZERO
            if current_volume == FADER_ZERO:
                self.loopFadeStates[loop_state_name]['state'] = LOOP_FADE_STATE.FULL_VOLUME
            else:
                self.schedule_message(1, self.fadeLoop, {"track_index": track_index, "loop_state_name": loop_state_name})
            self.set_track_volume({"index": track_index, "value": current_volume})
        elif self.loopFadeStates[loop_state_name]['state'] == LOOP_FADE_STATE.FADING_OUT:
            current_volume = current_volume - self.fadeSpeed * FADE_AMOUNT
            if current_volume < 0:
                current_volume = 0
            if current_volume == 0:
                self.loopFadeStates[loop_state_name]['state'] = LOOP_FADE_STATE.VOLUME_ALL_DOWN
                self.schedule_message(1, self.stop_loops_on_track, track_index)
            else:
                self.schedule_message(1, self.fadeLoop, {"track_index": track_index, "loop_state_name": loop_state_name})
            self.set_track_volume({"index": track_index, "value": current_volume})

    def stop_loop(self, note):
        is_bank_a = note < Channel_1_Note.LOOP9
        track_index = self.track_processor.loop_tracks[note]
        loop_state_name = f'LOOP{note + 1}'
        if is_bank_a == False:
            #offset for bank b
            track_index + track_index + 1
        if self.fadeLoops:
            self.loopFadeStates[loop_state_name]['state'] = LOOP_FADE_STATE.FADING_OUT
            self.fadeLoop({"track_index": track_index, "loop_state_name": loop_state_name})
        else:
            self.stop_loops_on_track(self.track_processor.loop_tracks[note])

    def set_track_volume(self, data):
        self.song.tracks[data['index']].mixer_device.volume.value = data['value']

    def set_track_send(self, data):
        if data['is_return'] == True:
            self.song.return_tracks[data['index']].mixer_device.sends[data['send_index']].value = data['value']
        else:
            self.song.tracks[data['index']].mixer_device.sends[data['send_index']].value = data['value']

    def set_output_routing_type(self, data):
        if data['is_return'] == True:
            self.song.return_tracks[data['index']].output_routing_type = data['output_routing_type']
        else:
            self.song.tracks[data['index']].output_routing_type = data['output_routing_type']

    def set_output_routing_channel(self, data):
        if data['is_return'] == True:
            self.song.return_tracks[data['index']].output_routing_channel = data['output_routing_channel']
        else:
            self.song.tracks[data['index']].output_routing_channel = data['output_routing_channel']
        
        
    def stop_loops_on_track(self, track_index):
        self.song.tracks[track_index].stop_all_clips(False)

    def get_handler_by_identifier(self, identifier: str):
        """Returns the first handler with matching class_identifier or None if not found."""
        return next(
            (handler for handler in self.handlers if handler.class_identifier == identifier),
            None  # Default if not found
        )
    def clear_api(self):
        self.osc_server.clear_handlers()
        for handler in self.handlers:
            handler.clear_api()

    def tick(self):
        """Called once per 100ms 'tick'"""
        logger.debug("Tick...")
        self.osc_server.process()
        self.schedule_message(1, self.tick)

    def reload_imports(self):
        try:
            importlib.reload(abletonosc.application)
            importlib.reload(abletonosc.clip)
            importlib.reload(abletonosc.clip_slot)
            importlib.reload(abletonosc.device)
            importlib.reload(abletonosc.handler)
            importlib.reload(abletonosc.osc_server)
            importlib.reload(abletonosc.scene)
            importlib.reload(abletonosc.song)
            importlib.reload(abletonosc.track)
            importlib.reload(abletonosc.view)
            importlib.reload(abletonosc)
        except Exception as e:
            exc = traceback.format_exc()
            logging.warning(exc)

        self.clear_api()
        self.init_api()
        logger.info("Reloaded code")

    def disconnect(self):
        logger.info("Disconnecting...")
        self.stop_logging()
        self.osc_server.shutdown()
        super().disconnect()