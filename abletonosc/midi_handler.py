import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_CC_TYPE
import logging

logger = logging.getLogger("abletonosc")

class MidiHandler:
    def __init__(self, c_instance):
        super(CC_Logger, self).__init__(c_instance)
        self._cc_listeners = []
        self.log_message("CC Logger initialized - Ready to receive MIDI CC")
        self._setup_cc_listeners()

    def send_midi_cc(self, channel, cc_num, value):
        """Send a MIDI CC message"""
        # Correct way to send MIDI in Ableton scripts
        self._send_midi(tuple([0xB0 | (channel & 0x0F), cc_num & 0x7F, value & 0x7F]))

    def send_midi_note(self, channel, note, velocity):
        """Send a MIDI Note message"""
        self._send_midi(tuple([0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F]))
            
    def _setup_cc_listeners(self):
        """Create listeners for all MIDI CC messages"""
        with self.component_guard():
            for channel in range(16):  # All MIDI channels
                for cc_num in range(128):  # All CC numbers
                    self._create_cc_listener(channel, cc_num)

    def _create_cc_listener(self, channel, cc_num):
        """Create and configure a single CC listener"""
        cc = SliderElement(MIDI_CC_TYPE, channel, cc_num)
        # Fixed: Now properly captures sender reference in the lambda
        cc.add_value_listener(
            lambda value, sender=cc: self._handle_cc(value, sender),
            identify_sender=True
        )
        self._cc_listeners.append(cc)

    def _handle_cc(self, value, sender):
        """Handle incoming CC messages"""
        channel = sender.message_channel() + 1  # Convert to 1-based channel
        cc_num = sender.message_identifier()
        self.log_message(
            f"CC CH{channel:02d} #{cc_num:03d} = {value:03d}"
        )
        if cc_num == 68:
            self.send_midi_cc(1, 69, value)

    def disconnect(self):
        """Clean up on shutdown"""
        for cc in self._cc_listeners:
            cc.remove_value_listener(self._handle_cc)
        super(CC_Logger, self).disconnect()
        self.log_message("CC Logger disconnected")