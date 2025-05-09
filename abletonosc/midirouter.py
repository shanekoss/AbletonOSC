from ableton.v2.control_surface import ControlSurface
from ableton.v2.control_surface.elements import ButtonElement, EncoderElement
from ableton.v2.control_surface.input_control_element import MIDI_CC_TYPE, MIDI_NOTE_TYPE, MIDI_PB_TYPE, MIDI_SYSEX_TYPE
from ableton.v2.base import task
import Live
import logging

class MidiRouter(ControlSurface):
    """Complete MIDI router with proper SysEx handling"""
    
    def __init__(self, c_instance):
        super(MidiRouter, self).__init__(c_instance)
        self._c_instance = c_instance
        self._sysex_identity_request = bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
        self.logger = logging.getLogger("abletonosc")
        self.logger.info("MidiRouter INIT!!!")
        with self.component_guard():
            self._setup_midi_mapping()
            self._setup_midi_receivers()
            self._setup_midi_senders()
            self.logger.info("MidiRouter with SysEx ready")
            self._tasks.add(task.run(self._post_init))
    
    def _post_init(self):
        """Called after initialization is complete"""
        self.logger.info("MidiRouter ready")
        self._send_midi_test_message()

    def _setup_midi_mapping(self):
        """Setup MIDI mapping including SysEx"""
        self._receiving_channel = 0  # OMNI mode
        self._sending_channel = 0
    
    def _setup_midi_receivers(self):
        """Create elements for receiving MIDI"""
        # Standard MIDI receivers
        self._note_receiver = ButtonElement(True, MIDI_NOTE_TYPE, 0, 0, name='Note_Receiver')
        self._note_receiver.add_value_listener(self._on_note_message, identify_sender=True)
        
        self._cc_receiver = EncoderElement(MIDI_CC_TYPE, 0, 0, 
                                        map_mode=Live.MidiMap.MapMode.absolute, 
                                        name='CC_Receiver')
        self._cc_receiver.add_value_listener(self._on_cc_message, identify_sender=True)
        
        self._pb_receiver = EncoderElement(MIDI_PB_TYPE, 0, 0,
                                         map_mode=Live.MidiMap.MapMode.absolute,
                                         name='PB_Receiver')
        self._pb_receiver.add_value_listener(self._on_pitch_bend, identify_sender=True)
        
        # SysEx receiver element
        self._sysex_receiver = ButtonElement(True, MIDI_SYSEX_TYPE, 0, 0, name='SysEx_Receiver')
        self._sysex_receiver.add_value_listener(self._on_sysex_message, identify_sender=True)
    
    def _setup_midi_senders(self):
        """Setup elements for sending MIDI including SysEx"""
        self._note_sender = ButtonElement(True, MIDI_NOTE_TYPE, 0, 0, name='Note_Sender')
        self._cc_sender = EncoderElement(MIDI_CC_TYPE, 0, 0,
                                       map_mode=Live.MidiMap.MapMode.absolute,
                                       name='CC_Sender')
        self._pb_sender = EncoderElement(MIDI_PB_TYPE, 0, 0,
                                       map_mode=Live.MidiMap.MapMode.absolute,
                                       name='PB_Sender')
        # SysEx sender element
        self._sysex_sender = ButtonElement(True, MIDI_SYSEX_TYPE, 0, 0, name='SysEx_Sender')
    
    def build_midi_map(self, midi_map_handle):
        self.logger.info("BUILDING THE FUCKING MIDI MAP!")
        """Setup MIDI mappings including SysEx"""
        script_handle = self._c_instance.handle()
        Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 0, 0)
        Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, 0, 0)
        Live.MidiMap.forward_midi_pitchbend(script_handle, midi_map_handle, 0)
    
    def receive_midi(self, midi_bytes):
        """Handle incoming MIDI including SysEx"""
        self.logger.info("MIDI MESSAGE RECEIVED!")
        self.logger.info(midi_bytes)
        # Check for SysEx message (0xF0)
        if midi_bytes[0] == 0xF0:
            self._handle_sysex(midi_bytes)
            return  # Prevent default handling that causes the warning
            
        # Standard MIDI messages
        status_byte = midi_bytes[0]
        message_type = status_byte & 0xF0
        channel = (status_byte & 0x0F) + 1
        
        if message_type == 0xC0:  # Program change
            program = midi_bytes[1]
            self.logger.info(f"Program Change: {program} on {channel}")
        
        super(MidiRouter, self).receive_midi(midi_bytes)
    
    def _handle_sysex(self, sysex_bytes):
        """Process incoming SysEx messages without triggering warnings"""
        try:
            # Convert to hex string for display
            hex_str = ' '.join(f'{b:02X}' for b in sysex_bytes)
            self.logger.info(f"SysEx: {hex_str}")
            
            # Example: Respond to identity request
            if sysex_bytes == self._sysex_identity_request:
                response = bytes([0xF0, 0x7E, 0x00, 0x06, 0x02, 0x00, 0x20, 0x29, 0x01, 0x00, 0x00, 0x01, 0xF7])
                self._send_sysex(response)
            
        except Exception as e:
            self.logger.info(f"SysEx Error: {str(e)}")

    def _on_sysex_message(self, value, sender):
        """Handle SysEx from dedicated element"""
        # This gets called if SysEx is routed to our element
        self.logger.info("SysEx via Element received")

    def _send_sysex(self, sysex_bytes):
        """Send raw SysEx message"""
        try:
            self._c_instance.send_midi(sysex_bytes)
            hex_str = ' '.join(f'{b:02X}' for b in sysex_bytes)
            self.logger.info(f"Sent SysEx: {hex_str}")
        except Exception as e:
            self.logger.info(f"SysEx Send Error: {str(e)}")
    
    def _on_note_message(self, value, sender):
        note = sender.identifier
        velocity = value if value > 0 else 0
        self.logger.info(f"Note {'ON' if value > 0 else 'OFF'}: {note} Vel: {velocity}")
        self._send_note(note, velocity)
    
    def _on_cc_message(self, value, sender):
        cc_num = sender.identifier
        self.logger.info(f"CC: {cc_num} = {value}")
        self._send_cc(cc_num, value)
    
    def _on_pitch_bend(self, value, sender):
        self.logger.info(f"Pitch Bend: {value}")
        self._send_pitch_bend(value)

    def _send_midi_test_message(self):
        self._send_note(60, 127)
        self._send_cc(1, 64)
        self._send_pitch_bend(8192)
        self._send_program_change(1)
        # Example SysEx message (generic inquiry)
        test_sysex = bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
        self._send_sysex(test_sysex)
    
    def _send_note(self, note, velocity, channel=1):
        self._note_sender.send_value(note, velocity, channel-1)
    
    def _send_cc(self, cc_num, value, channel=1):
        self._cc_sender.send_value(cc_num, value, channel-1)
    
    def _send_pitch_bend(self, value, channel=1):
        self._pb_sender.send_value(value, channel=channel-1)
    
    def _send_program_change(self, program, channel=1):
        status_byte = 0xC0 + (channel - 1)
        self._c_instance.send_midi((status_byte, program))
    
    def disconnect(self):
        self.logger.info("MidiRouter shutting down")
        super(MidiRouter, self).disconnect()