from typing import Tuple, Any, Callable, Optional, List
from .abletonosc.constants import LOOPTRACK_NAMES, BANK_A_TEMPO, BANK_B_OFFSET, Channel_1_CC, Channel_1_Note, SYSEX_PREFIX, LOOP_STATE, FADER_ZERO, STATE, ROUTING, PRESET_INCLUDE_TRACKS, RETURN_TRACKS, RETURNS

import Live # type: ignore
import logging

class TrackProcessor():
    def __init__(self):
        self.class_identifier = "track_processor"
        self.loop_tracks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.manager = None
        self.logger = None
        self.track_listeners = []
        self.param_listeners = []

    def get_portal_presets(self):
        app = Live.Application.get_application()
        project = app.browser.current_project
        
        for child in project.children:
            if child.name == "Presets":
                for subchild in child.children:
                    if subchild.name == "PortalFX":
                        for preset in subchild.children:
                            self.logger.info(f"Preset found: {preset.name}")
                        return
        
        # self.logger.error("PortalFX folder was not found: BAD!")
            # # If you want to go deeper into the hierarchy:
            # if hasattr(child, 'children'):
            #     for subchild in child.children:
            #         self.logger.info(subchild.name)
            #         if subchild.name == "sn 2 hard.dup6_01.adv":
            #             app.browser.load_item(subchild)

    def processTracks(self, tracks: List[Live.Track.Track]):
        for index, track in enumerate(tracks):
            if track.name in PRESET_INCLUDE_TRACKS:
                PRESET_INCLUDE_TRACKS[track.name]['index'] = index

            if track.name == BANK_A_TEMPO:
                self.manager.bankATempoIndex = index
                continue
            elif track.name == "STATE":
                self.manager.state_index = index
                listener = lambda param = track.devices[0].parameters[STATE.SPLITS]: self._on_routing_change(param)
                track.devices[0].parameters[STATE.SPLITS].add_value_listener(listener)
                self.param_listeners.append((track.devices[0].parameters[STATE.SPLITS], listener))
                continue
            elif track.name in LOOPTRACK_NAMES:
                loop_index = LOOPTRACK_NAMES.index(track.name)
                if loop_index != -1:
                    if loop_index >= len(self.loop_tracks):
                        self.logger.error(f"Loop Index ${loop_index} is out of range! BAD!")
                    else:
                        track.mixer_device.volume.value = FADER_ZERO
                        self.loop_tracks[loop_index] = index
                        listener = lambda t=track, l=loop_index: self._on_playing_slot_index_changed(t, l)
                        track.add_playing_slot_index_listener(listener)
                        self.track_listeners.append((track, listener))  # Store for cleanup
                    continue

    def processReturnTracks(self, return_tracks: List[Live.Track.Track]):
        for index, track in enumerate(return_tracks):
            if track.name in RETURN_TRACKS:
                self.logger.info(f"Setting {track.name} index to {index}")
                RETURN_TRACKS[track.name]['index'] = index
                self.logger.info(RETURN_TRACKS[track.name])
            if track.name == "A-TIDEa":
                self.manager.tide_a_index = index
                for param_index, parameter in enumerate(track.devices[0].parameters):
                    if parameter.name == "tidepgm":
                        self.manager.tide_pgm_index = param_index
                    if parameter.name == "tidePresetName":
                        #TODO: do we need this index anymore if we are passing the param?
                        self.manager.tide_preset_name_index = param_index
                        listener = lambda param = parameter: self._on_tide_name_changed(param)
                        parameter.add_value_listener(listener)
                        self.param_listeners.append((parameter, listener))
            elif track.name == "B-PORTAL":
                self.manager.portal_index = index
                # self.logger.info(f"Current variation: {track.devices[0].selected_variation_index}")
                # track.devices[0].selected_variation_index = track.devices[0].selected_variation_index + 1
                for param_index, parameter in enumerate(track.devices[0].parameters):
                    if parameter.name == "Mvmt Y":
                        self.manager.movement_y_index = param_index
                    elif parameter.name == "Mvmt X":
                        self.manager.movement_x_index = param_index
                    elif parameter.name == "Mvmt Wet/Dry":
                        self.manager.movement_wet_dry_index = param_index
                    elif parameter.name == "Portal Macro1":
                        self.manager.portal_1_index = param_index
                    elif parameter.name == "Portal Macro2":
                        self.manager.portal_2_index = param_index
                    elif parameter.name == "Portal Reverse":
                        self.manager.portal_reverse_index = param_index
                    elif parameter.name == "Portal Wet/Dry":
                        self.manager.portal_wet_dry_index = param_index
                # current_project_children = Live.Browser.Browser.current_project
                # for param_index, child in enumerate(current_project_children):
                #     self.logger.info(child.name)
                # self.logger.info("looking!")
                # self.logger.info(f"found {dir(track.devices[0].chains[0].devices[2].view)}")
                for param_index, parameter in enumerate(track.devices[0].chains[0].devices[2].parameters):
                    #TODO: do we need this for preset recall?
                    # if parameter.name == "portalPGM":
                        # listener = lambda: self._on_portal_name_changed()
                        # parameter.add_value_listener(listener)
                        # self.param_listeners.append((parameter, listener))
                    if parameter.name == "portalName":
                        #TODO: do we need this index anymore if we are passing the param?
                        self.manager.portal_name_index = param_index
                        listener = lambda param  = parameter: self._on_portal_name_changed(param)
                        parameter.add_value_listener(listener)
                        self.param_listeners.append((parameter, listener))

    def set_routing(self, track_index, send_up, sends_down, output_routing_type, output_routing_channel, is_return = False):
        # self.logger.info(self.manager.song.tracks[2].output_routing_type.display_name) # Main, Ext. Out, Track, Sends Only
        # self.logger.info(self.manager.song.tracks[2].output_routing_channel.display_name) # 1/2, 3/4, etc
        if output_routing_type is not None:
            found_output_routing = False
            tracks = self.manager.song.tracks
            if is_return is True:
                tracks = self.manager.song.return_tracks
            for output_type in tracks[track_index].available_output_routing_types:
                # self.logger.info(f"output_type {output_type.display_name}")
                if output_type.display_name == output_routing_type:
                    self.manager.schedule_message(1, self.manager.set_output_routing_type, {"index": track_index, "output_routing_type": output_type, "is_return": is_return })
                    found_output_routing = True
                    break
            if found_output_routing == False:
                self.log.error(f"Failed to find output routing type: {output_routing_type}")
        if output_routing_channel is not None:
            self.manager.schedule_message(1, self.set_sub_routing, {"tracks": tracks, "track_index": track_index, "output_routing_channel": output_routing_channel, "is_return": is_return, "timeout": 0})
                # self.logger.info(f"output_routing_channel {output_routing_channel.display_name}")
        #STRINGS ONLY
        # for output_routing in self.manager.song.tracks[2].output_routings:
        #     self.logger.info(f"output_routing {output_routing}")
        # for output_sub_routing in self.manager.song.tracks[2].output_sub_routings:
        #     self.logger.info(f"output_sub_routing {output_sub_routing}")
        # self.logger.info(self.manager.song.tracks[2].output_routing_type.display_name) # Main, Ext. Out, Track, Sends Only
        # self.logger.info(self.manager.song.tracks[2].output_routing_channel.display_name) # 1/2, 3/4, etc
        if send_up is not None:
            self.manager.schedule_message(1, self.manager.set_track_send, {"index": track_index, "send_index": send_up, "value": 1.0, "is_return": is_return})
        for send in sends_down:
            self.manager.schedule_message(1, self.manager.set_track_send, {"index": track_index, "send_index": send, "value": 0.0, "is_return": is_return})

    def set_sub_routing(self, data):
        if len(data['tracks'][data['track_index']].available_output_routing_channels) == 0:
            self.logger.info("Not ready yet - gonna wait another tick!")
            data['timeout'] = data['timeout'] + 1
            if data['timeout'] < 10:
                self.manager.schedule_message(1, self.set_sub_routing, data)
            else:
                self.logger.error(f"timed out waiting for available routing channels for track index: {data['track_index']}")
            return
        
        found_output_channel= False
        for output_channel in data['tracks'][data['track_index']].available_output_routing_channels:
            if output_channel.display_name == data['output_routing_channel']:
                self.manager.schedule_message(1, self.manager.set_output_routing_channel, {"index": data['track_index'], "output_routing_channel": output_channel, "is_return": data['is_return']})
                found_output_channel= True
                break
        if found_output_channel == False:
            self.logger.error(f"Failed to find output routing channel: {data['output_routing_channel']}")

    def _on_routing_change(self, param):
        selection = param.value
        if selection == ROUTING.STEREO:
            self.set_routing(PRESET_INCLUDE_TRACKS["bass"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.BASS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["piano"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.KEYS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH1"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.KEYS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH2"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.KEYS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH3"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.KEYS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["mic"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.VOCAL]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["vocoder"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.VOCAL]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["violin"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["violin2"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["Sampler"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.KEYS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["BANKA"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.LOOPS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["BANKB"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.LOOPS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["FOOT"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.KEYS]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["FOOTLOOPS"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [RETURN_TRACKS[RETURNS.LOOPS]['index']], "Sends Only", None)
            self.set_routing(RETURN_TRACKS[RETURNS.TIDE]['index'], None, [], "Main", None, True)
            self.set_routing(RETURN_TRACKS[RETURNS.PORTAL]['index'], None, [], "Main", None, True)

            self.set_routing(RETURN_TRACKS[RETURNS.LOOPS]['index'], None, [], "Main", None, True)
            self.set_routing(RETURN_TRACKS[RETURNS.KEYS]['index'], None, [], "Main", None, True)
            self.set_routing(RETURN_TRACKS[RETURNS.VOCAL]['index'], None, [], "Main", None, True)
            self.set_routing(RETURN_TRACKS[RETURNS.BASS]['index'], None, [], "Main", None, True)

        elif selection == ROUTING.RME or selection == ROUTING.RME_OPTICAL:
            self.set_routing(PRESET_INCLUDE_TRACKS["bass"]['index'], RETURN_TRACKS[RETURNS.BASS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["piano"]['index'], RETURN_TRACKS[RETURNS.KEYS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH1"]['index'], RETURN_TRACKS[RETURNS.KEYS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH2"]['index'], RETURN_TRACKS[RETURNS.KEYS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH3"]['index'], RETURN_TRACKS[RETURNS.KEYS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["mic"]['index'], RETURN_TRACKS[RETURNS.VOCAL]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["vocoder"]['index'], RETURN_TRACKS[RETURNS.VOCAL]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["violin"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["violin2"]['index'], RETURN_TRACKS[RETURNS.STEREO]['index'], [], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["Sampler"]['index'], RETURN_TRACKS[RETURNS.KEYS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["BANKA"]['index'], RETURN_TRACKS[RETURNS.LOOPS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["BANKB"]['index'], RETURN_TRACKS[RETURNS.LOOPS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["FOOT"]['index'], RETURN_TRACKS[RETURNS.KEYS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["FOOTLOOPS"]['index'], RETURN_TRACKS[RETURNS.LOOPS]['index'], [RETURN_TRACKS[RETURNS.STEREO]['index']], "Sends Only", None)
            self.set_routing(RETURN_TRACKS[RETURNS.TIDE]['index'], None, [], "Sends Only", None, True)
            self.set_routing(RETURN_TRACKS[RETURNS.PORTAL]['index'], None, [], "Sends Only", None, True)

            if selection == ROUTING.RME:
                # set loops, keys, vocal and bass to analog
                self.set_routing(RETURN_TRACKS[RETURNS.LOOPS]['index'], None, [], "Ext. Out", "3/4", True)
                self.set_routing(RETURN_TRACKS[RETURNS.KEYS]['index'], None, [], "Ext. Out", "5/6", True)
                self.set_routing(RETURN_TRACKS[RETURNS.VOCAL]['index'], None, [], "Ext. Out", "7", True)
                self.set_routing(RETURN_TRACKS[RETURNS.BASS]['index'], None, [], "Ext. Out", "8", True)
            else:
                # set loops, keys, vocal and bass to optical
                self.set_routing(RETURN_TRACKS[RETURNS.LOOPS]['index'], None, [], "Ext. Out", "11/12", True)
                self.set_routing(RETURN_TRACKS[RETURNS.KEYS]['index'], None, [], "Ext. Out", "13/14", True)
                self.set_routing(RETURN_TRACKS[RETURNS.VOCAL]['index'], None, [], "Ext. Out", "15", True)
                self.set_routing(RETURN_TRACKS[RETURNS.BASS]['index'], None, [], "Ext. Out", "16", True)
            
        elif selection == ROUTING.DANTE:
            self.set_routing(PRESET_INCLUDE_TRACKS["bass"]['index'], None, [RETURN_TRACKS[RETURNS.BASS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Bass Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["piano"]['index'], None, [RETURN_TRACKS[RETURNS.KEYS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Piano Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH1"]['index'], None, [RETURN_TRACKS[RETURNS.KEYS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Keys 1 Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH2"]['index'], None, [RETURN_TRACKS[RETURNS.KEYS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Keys 2 Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["SYNTH3"]['index'], None, [RETURN_TRACKS[RETURNS.KEYS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Keys 3 Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["mic"]['index'], None, [RETURN_TRACKS[RETURNS.VOCAL]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Vocal Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["vocoder"]['index'], None, [RETURN_TRACKS[RETURNS.VOCAL]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Vocoder Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["violin"]['index'], None, [RETURN_TRACKS[RETURNS.STEREO]['index']], "Violin Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["violin2"]['index'], None, [RETURN_TRACKS[RETURNS.STEREO]['index']], "Violin Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["Sampler"]['index'], None, [RETURN_TRACKS[RETURNS.KEYS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Violin Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["BANKA"]['index'], None, [RETURN_TRACKS[RETURNS.LOOPS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Loops 1 Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["BANKB"]['index'], None, [RETURN_TRACKS[RETURNS.LOOPS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Loops 2 Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["FOOT"]['index'], None, [RETURN_TRACKS[RETURNS.LOOPS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Foot Loops Stereo", None)
            self.set_routing(PRESET_INCLUDE_TRACKS["FOOTLOOPS"]['index'], None, [RETURN_TRACKS[RETURNS.LOOPS]['index'], RETURN_TRACKS[RETURNS.STEREO]['index']], "Foot Loops Stereo", None)
            self.set_routing(RETURN_TRACKS[RETURNS.TIDE]['index'], None, [], "Tide/FX Stereo", None, True)
            self.set_routing(RETURN_TRACKS[RETURNS.PORTAL]['index'], None, [], "Tide/FX Stereo", None, True)
        else:
            self.logger.error(f"Invalid routing option: {selection}")
    
    def _on_playing_slot_index_changed(self, track, loop_index):
        loop_state = LOOP_STATE.STOPPED
        slot_index = track.playing_slot_index
        if slot_index >= 0:
            #TODO: do we want to verify slot_index matches the loop bank expected?
            loop_state = LOOP_STATE.PLAYING
        self.manager.send_midi_note(0, loop_index, loop_state)

    def _on_portal_name_changed(self, param):
        portal_name = param.value_items[0]
        portal_name_bytes = portal_name.encode('ascii', errors='ignore')
        sysex_message = bytes([SYSEX_PREFIX.PORTAL_NAME]) + portal_name_bytes
        self.manager.send_sysex(sysex_message)

    def _on_tide_name_changed(self, param):
        tide_name = param.value_items[0]
        tide_name_bytes = tide_name.encode('ascii', errors='ignore')
        sysex_message = bytes([SYSEX_PREFIX.TIDE_NAME]) + tide_name_bytes
        self.manager.send_sysex(sysex_message)

    def setBankALoops(self, new_bank_a_index, should_send_midi = False):
        for loop_track_index in range(1, 9):
            track_index = self.manager.bankATempoIndex + loop_track_index
            self.manager.song.tracks[track_index].stop_all_clips(False)
        self.manager.currentBankAIndex = new_bank_a_index
        if self.manager.currentBankAIndex >= len(self.manager.song.tracks[self.manager.bankATempoIndex].clip_slots):
            self.logger.warning(f"bank a index {self.manager.currentBankAIndex} is out of range!")
        else:
            if self.manager.song.tracks[self.manager.bankATempoIndex].clip_slots[self.manager.currentBankAIndex].has_clip:
                self.manager.song.tempo = float(self.manager.song.tracks[self.manager.bankATempoIndex].clip_slots[self.manager.currentBankAIndex].clip.name)
            else:
                self.logger.warning(f"Clip slot {self.manager.currentBankAIndex} for bankA has no tempo clip!")
            self.sendBankANames(self.manager.currentBankAIndex)
            if should_send_midi:
                self.manager.send_midi_cc(0, Channel_1_CC.BANK_A_SELECT, self.manager.currentBankAIndex)

    def setBankBLoops(self, new_bank_b_index, should_send_midi = False):
        for loop_track_index in range(9, 17):
            track_index = self.manager.bankATempoIndex + loop_track_index
            self.manager.song.tracks[track_index].stop_all_clips(False)
        self.manager.currentBankBIndex = new_bank_b_index
        self.sendBankBNames(self.manager.currentBankBIndex)
        if should_send_midi:
            self.manager.send_midi_cc(0, Channel_1_CC.BANK_B_SELECT, self.manager.currentBankBIndex)

    def sendBankANames(self, bank_a_index):
        for index, track_index in enumerate(self.loop_tracks[:8]):
            clip_name =" "
            if self.manager.song.tracks[track_index].clip_slots[bank_a_index].clip != None:
                clip_name = self.manager.song.tracks[track_index].clip_slots[bank_a_index].clip.name
            clip_name_bytes = clip_name.encode('ascii', errors='ignore')
            sysex_message = bytes([SYSEX_PREFIX.LOOP_NAMES, index]) + clip_name_bytes
            self.manager.send_sysex(sysex_message)

    def sendBankBNames(self, bank_b_index):
        for index, track_index in enumerate(self.loop_tracks[8:]):
            clip_name =" "
            if bank_b_index < len(self.manager.song.tracks[track_index].clip_slots) and self.manager.song.tracks[track_index].clip_slots[bank_b_index].clip != None:
                clip_name = self.manager.song.tracks[track_index].clip_slots[bank_b_index].clip.name
            clip_name_bytes = clip_name.encode('ascii', errors='ignore')
            sysex_message = bytes([SYSEX_PREFIX.LOOP_NAMES, index + BANK_B_OFFSET]) + clip_name_bytes
            self.manager.send_sysex(sysex_message)

    def disconnect(self):
        """Remove all listeners on script shutdown"""
        for track, listener in self.track_listeners:
            if track.playing_slot_index_has_listener(listener):
                track.remove_playing_slot_index_listener(listener)
        self.track_listeners = []  # Clear the list

        for param, listener in self.param_listeners:
            if param.value_has_listener(listener):
                param.remove_value_listener(listener)
        self.param_listeners = []  # Clear the list