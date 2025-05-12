from ableton.v2.control_surface import ControlSurface
from ableton.v2.control_surface.elements import SliderElement, ButtonElement, EncoderElement
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_PB_TYPE, MIDI_NOTE_TYPE

from . import abletonosc
from .track_processor import TrackProcessor
import importlib
import traceback
import logging
import os
import Live

logger = logging.getLogger("abletonosc")

class Manager(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._c_instance = c_instance
        self.log_level = "info"

        # MIDI Handling Setup
        self._cc_listeners = []
        self._note_listeners = []
        self._sysex_listeners = []
        try:
            self.osc_server = abletonosc.OSCServer()
            self.schedule_message(0, self.tick)
            self.start_logging()
            self.init_api()
            self._setup_midi_handling()

            logger.info("AbletonOSC: Listening for OSC on port %d" % abletonosc.OSC_LISTEN_PORT)
        except OSError as msg:
            logger.error("Couldn't bind to port %d (%s)" % (abletonosc.OSC_LISTEN_PORT, msg))

        self.track_processor = TrackProcessor()
        self.track_processor.manager = self
        self.track_processor.logger = logger
        self.track_processor.processTracks(self.song.tracks)

    def handle_volume_cc(self, value):
        logger.info(f"Volume CC changed to {value}")

    def _setup_midi_handling(self):
        """Initialize MIDI handling components"""
        # Enable receiving all MIDI messages
        self._c_instance.set_feedback_channels(list(range(16)))
        with self.component_guard():
            logger.info("Create listeners for all MIDI CC messages")
            for channel in range(16):  # All MIDI channels
                for cc_num in range(128):  # All CC numbers
                    self.register_cc_listener(channel, cc_num)

    def receive_midi(self, midi_bytes):
        logger.info("MIDI RECEIVED!")
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
        channel = sender.message_channel() + 1  # Convert to 1-based channel
        cc_num = sender.message_identifier()
        self.processCCMessage(channel, cc_num, value)

        # test_sysex = bytes([cc_num, value])
        # self.send_sysex(test_sysex)

    def _handle_note(self, channel, note_number, is_on, velocity):
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
        # Fixed: Now properly captures sender reference in the lambda
        cc.add_value_listener(
            lambda value, sender=cc: self._handle_cc(value, sender),
            identify_sender=True
        )
        self._cc_listeners.append(cc)

    def register_note_listener(self, channel, note_number, callback):
        logger.info("Register callback for Note messages (channel: 0-15)")

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

    # TODO: move these process functions to another file!
    def processCCMessage(self, channel, cc_num, value):
        handled = False
        if channel == 1:
            if cc_num == 16:
                handled = True
                bankAIndex = value
                if bankAIndex >= len(self.song.tracks[self.track_processor.bankATempoIndex].clip_slots):
                    logger.warning(f"bank a index {bankAIndex} is out of range!")
                else:
                    self.song.tracks[self.track_processor.bankATempoIndex].clip_slots[value].fire()
                    self.track_processor.sendBankANames(value)
            if cc_num == 17:
                handled = True
                bankBIndex = value
                self.track_processor.sendBankBNames(value)
        if handled == False:
            logger.info(f"Unhandled CC CH{channel:02d} #{cc_num:03d} = {value:03d}")
    
    def processNoteMessage(self, channel, note, velocity):
        handled = False
        if channel == 1:
            if 0 <= note <= 15:
                if velocity == 1:
                    handled = True
                    self.song.tracks[self.track_processor.loop_tracks[note]].clip_slots[self.track_processor.bankATempoIndex].fire()
                    self.logger.info(f"Stop Loop{note+1}")
                elif velocity == 2:
                    handled = True
                    # TODO: do we really want to do this this way?
                    self.song.tracks[self.track_processor.loop_tracks[note]].stop_all_clips()
                    self.logger.info(f"Fire Loop{note+1}")

        if handled == False:
            logger.info(f"Unhandled Note CH{channel:02d} #{note:03d} = {velocity:03d}")