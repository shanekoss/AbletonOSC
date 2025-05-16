import json
import os
from collections import OrderedDict
from pathlib import Path
from .abletonosc.constants import PRESET_INCLUDE_TRACKS, MIDI_TRANSPOSER_DEVICE

import logging

class PresetManager:
    """
    A remote MIDI script for Ableton Live that handles saving and loading
    Live sets as JSON presets.
    """
    
    def __init__(self, c_instance):
        """
        Initialize the preset manager.
        
        Args:
            c_instance: The control surface instance from Ableton
        """
        self._c_instance = c_instance
        self._presets_dir = os.path.expanduser("~/AbletonPresets")
        self.preset_path = os.path.join(self._presets_dir, "LaurieRigPresets.json")
        self.logger = None
        
        # Ensure presets directory exists
        os.makedirs(self._presets_dir, exist_ok=True)
        
        # Initialize presets file if it doesn't exist
        
    def initialize_presets_file(self):
        """Ensure the presets file exists with an empty array if it doesn't."""
        if not os.path.exists(self.preset_path):
            try:
                with open(self.preset_path, 'w') as f:
                    json.dump([], f)
                self.logger.info("Created new presets file with empty array")
            except Exception as e:
                self.logger.error(f"Error creating presets file: {str(e)}")
                raise
        
    def disconnect(self):
        """Clean up when disconnecting."""
        pass
    
    # --- Preset Management Methods ---
    
    def save_current_set_as_preset(self, preset_index):
        """
        Save the current Live set as a JSON preset at the specified index.
        
        Args:
            preset_index (int): Index to save the preset at
        """
        try:
            live_set = self._c_instance.song()
            preset_data = self._extract_set_data(live_set)
            
            # Initialize presets array
            presets = []
            
            # Load existing presets if file exists and is valid
            if os.path.exists(self.preset_path):
                try:
                    with open(self.preset_path, 'r') as f:
                        presets = json.load(f, object_pairs_hook=OrderedDict)
                        if not isinstance(presets, list):  # If file exists but isn't an array
                            presets = []
                except (json.JSONDecodeError, IOError):
                    presets = []
            
            # Expand array if needed
            while len(presets) <= preset_index:
                presets.append(None)
            
            # Save preset at index
            presets[preset_index] = preset_data
            
            # Save back to file
            with open(self.preset_path, 'w') as f:
                json.dump(presets, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving preset: {str(e)}")
            return False
    
    def load_preset_into_set(self, preset_index):
        """
        Load a JSON preset from the specified index into the current Live set.
        
        Args:
            preset_index (int): Index of the preset to load
        """
        try:
            if not os.path.exists(self.preset_path):
                self.logger.error("Preset file not found")
                return False
                
            with open(self.preset_path, 'r') as f:
                try:
                    presets = json.load(f, object_pairs_hook=OrderedDict)
                    if not isinstance(presets, list):
                        self.logger.error("Preset file is corrupted - not an array")
                        return False
                        
                    if preset_index >= len(presets):
                        self.logger.error(f"Preset index {preset_index} does not exist!")
                        return False
                    
                    preset_data = presets[preset_index]
                    if preset_data is None:
                        self.logger.error(f"No preset exists at index {preset_index}!")
                        return False
                    
                    live_set = self._c_instance.song()
                    self._apply_set_data(live_set, preset_data)
                    
                    return True
                except json.JSONDecodeError:
                    self.logger.error("Preset file is corrupted - invalid JSON")
                    return False
        except Exception as e:
            self.logger.error(f"Error loading preset: {str(e)}")
            return False
        
    def get_available_presets(self):
        """Return a list of available presets."""
        presets = []
        for file in Path(self._presets_dir).glob("*.json"):
            presets.append(file.stem)
        return sorted(presets)
    
    # --- Data Extraction Methods ---
    
    def _extract_set_data(self, live_set):
        """
        Extract relevant data from the Live set to save as a preset.
        
        Args:
            live_set: The Live set object
            
        Returns:
            dict: The extracted preset data
        """
        data = OrderedDict()
        
        # Basic set information
        data['name'] = live_set.name
        data['tempo'] = live_set.tempo
        data['time_signature'] = {
            'numerator': live_set.signature_numerator,
            'denominator': live_set.signature_denominator
        }
        data['loop'] = {
            'start': live_set.loop_start,
            'length': live_set.loop_length,
            'enabled': live_set.loop
        }
        
        # Tracks
        data['tracks'] = []
        for track in live_set.tracks:
            track_data = self._extract_track_data(track)
            if track_data != None:
                data['tracks'].append(track_data)
        return data
    
    def _extract_track_data(self, track):
        """Extract data from a single track."""
        foundTrack = next((element for element in PRESET_INCLUDE_TRACKS if element["name"] == track.name), None)
        if foundTrack is not None:
            track_data = OrderedDict()
            track_data['name'] = track.name
            track_data['mute'] = track.mute
            track_data['volume'] = track.mixer_device.volume.value
            track_data['sends'] = []
            for send in track.mixer_device.sends:
                param_data = {
                    'name': send.name,
                    'value': send.value,
                    'min': send.min,
                    'max': send.max,
                    'is_quantized': send.is_quantized
                }
                track_data['sends'].append(param_data)
            track_data['panning'] = track.mixer_device.panning.value
            if foundTrack["hasTransp"] == True:
                transpose_device = None
                for device in track.devices:
                    transpose_device = self._extract_device_data(device, MIDI_TRANSPOSER_DEVICE)
                    if transpose_device is not None:
                        break
                if transpose_device is None:
                    self.logger.warning(f"MidiTranpose device not found for {track.name}")
                else:
                    self.logger.info("BOOM")
                    self.logger.info(transpose_device)
                    track_data['transpose_device'] = transpose_device
            # # Devices
            # track_data['devices'] = []
            # for device in track.devices:
            #     device_data = self._extract_device_data(device)
            #     track_data['devices'].append(device_data)
                
            # # Clips
            # track_data['clips'] = []
            # for clip_slot in track.clip_slots:
            #     if clip_slot.has_clip:
            #         clip_data = self._extract_clip_data(clip_slot.clip)
            #         track_data['clips'].append(clip_data)
                    
            return track_data
        else:
            return None
    
    def _extract_device_data(self, device, device_name = None):
        """Extract data from a device."""
        device_data = OrderedDict()
        if device_name != None and device.name != device_name:
            return None
        device_data['name'] = device.name
        device_data['class_name'] = device.class_name
        device_data['type'] = device.type
        
        # Parameters
        device_data['parameters'] = []
        for param in device.parameters:
            param_data = {
                'name': param.name,
                'value': param.value,
                'min': param.min,
                'max': param.max,
                'is_quantized': param.is_quantized
            }
            device_data['parameters'].append(param_data)
                
        return device_data
    
    def _extract_clip_data(self, clip):
        """Extract data from a clip."""
        clip_data = OrderedDict()
        clip_data['name'] = clip.name
        clip_data['color'] = clip.color
        clip_data['length'] = clip.length
        clip_data['loop_start'] = clip.loop_start
        clip_data['loop_end'] = clip.loop_end
        clip_data['start_time'] = clip.start_time
        clip_data['end_time'] = clip.end_time
        # clip_data['warping'] = clip.warping
        # clip_data['warp_mode'] = clip.warp_mode
        # clip_data['gain'] = clip.gain
        
        # Notes (for MIDI clips)
        # if clip.is_midi_clip:
        #     clip_data['notes'] = []
        #     for note in clip.get_notes(0, 0, 128, clip.length):
        #         note_data = {
        #             'pitch': note[0],
        #             'start_time': note[1],
        #             'duration': note[2],
        #             'velocity': note[3],
        #             'mute': note[4]
        #         }
        #         clip_data['notes'].append(note_data)
                
        return clip_data
    
    # --- Data Application Methods ---
    
    def _apply_set_data(self, live_set, preset_data):
        """
        Apply preset data to the current Live set.
        
        Args:
            live_set: The Live set object
            preset_data (dict): The preset data to apply
        """
        # Basic set properties
        live_set.tempo = preset_data.get('tempo', live_set.tempo)
        
        time_sig = preset_data.get('time_signature', {})
        live_set.signature_numerator = time_sig.get('numerator')
        live_set.signature_denominator = time_sig.get('denominator')
        
        loop = preset_data.get('loop', {})
        live_set.loop_start = loop.get('start')
        live_set.loop_length = loop.get('length')
        live_set.loop = loop.get('enabled')
        
        # Tracks - this is simplified for the example
        # In a real implementation, you'd need to handle track creation/matching
        for i, track_data in enumerate(preset_data.get('tracks', [])):
            if i < len(live_set.tracks):
                self._apply_track_data(live_set.tracks[i], track_data)
    
    def _apply_track_data(self, track, track_data):
        """Apply data to a single track."""
        track.name = track_data.get('name', track.name)
        track.color = track_data.get('color', track.color)
        track.mute = track_data.get('mute', track.mute)
        track.solo = track_data.get('solo', track.solo)
        track.mixer_device.volume.value = track_data.get('volume', track.mixer_device.volume.value)
        track.mixer_device.panning.value = track_data.get('panning', track.mixer_device.panning.value)
        
        # Devices - simplified
        for i, device_data in enumerate(track_data.get('devices', [])):
            if i < len(track.devices):
                self._apply_device_data(track.devices[i], device_data)
    
    def _apply_device_data(self, device, device_data):
        """Apply data to a device."""
        # In a real implementation, you'd need to handle device creation/matching
        for param_data in device_data.get('parameters', []):
            for param in device.parameters:
                if param.name == param_data['name']:
                    param.value = param_data['value']
                    break
    
    def _apply_clip_data(self, clip, clip_data):
        """Apply data to a clip."""
        clip.name = clip_data.get('name', clip.name)
        clip.color = clip_data.get('color', clip.color)
        clip.loop_start = clip_data.get('loop_start', clip.loop_start)
        clip.loop_end = clip_data.get('loop_end', clip.loop_end)
        clip.start_time = clip_data.get('start_time', clip.start_time)
        clip.end_time = clip_data.get('end_time', clip.end_time)
        clip.warping = clip_data.get('warping', clip.warping)
        clip.warp_mode = clip_data.get('warp_mode', clip.warp_mode)
        clip.gain = clip_data.get('gain', clip.gain)
        
        if clip.is_midi_clip:
            notes = clip_data.get('notes', [])
            clip.remove_notes(0, 0, 128, clip.length)
            for note_data in notes:
                clip.set_notes((
                    note_data['pitch'],
                    note_data['start_time'],
                    note_data['duration'],
                    note_data['velocity'],
                    note_data['mute']
                ))