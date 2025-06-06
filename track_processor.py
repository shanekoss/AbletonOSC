from typing import Tuple, Any, Callable, Optional, List
from .abletonosc.constants import LOOPTRACK_NAMES, BANK_A_TEMPO, BANK_B_OFFSET, Channel_1_CC, Channel_1_Note, SYSEX_PREFIX, LOOP_STATE, FADER_ZERO

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
        
        self.logger.error("PortalFX folder was not found!!")
            # # If you want to go deeper into the hierarchy:
            # if hasattr(child, 'children'):
            #     for subchild in child.children:
            #         self.logger.info(subchild.name)
            #         if subchild.name == "sn 2 hard.dup6_01.adv":
            #             app.browser.load_item(subchild)

    def processTracks(self, tracks: List[Live.Track.Track]):
        for index, track in enumerate(tracks):
            if track.name == BANK_A_TEMPO:
                self.manager.bankATempoIndex = index
                continue
            elif track.name == "STATE":
                self.manager.state_index = index
                for param in self.manager.song.tracks[self.manager.state_index].devices[0].parameters:
                    self.logger.info(param.name)
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
            if track.name == "A-TIDEa":
                self.manager.tide_a_index = index
                for param_index, parameter in enumerate(track.devices[0].parameters):
                    if parameter.name == "tidepgm":
                        self.manager.tide_pgm_index = param_index
                    if parameter.name == "tidePresetName":
                        self.manager.tide_preset_name_index = param_index
                        listener = lambda: self._on_tide_name_changed()
                        parameter.add_value_listener(listener)
                        self.param_listeners.append((parameter, listener))
            elif track.name == "B-PORTAL":
                self.manager.portal_index = index
                # self.logger.info(f"Current variation: {track.devices[0].selected_variation_index}")
                # track.devices[0].selected_variation_index = track.devices[0].selected_variation_index + 1
                self.logger.info(dir(track.devices[0]));
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
                    if parameter.name == "portalPGM":
                        a = 1
                        # listener = lambda: self._on_portal_name_changed()
                        # parameter.add_value_listener(listener)
                        # self.param_listeners.append((parameter, listener))
                    if parameter.name == "portalName":
                        self.manager.portal_name_index = param_index
                        # listener = lambda: self._on_portal_name_changed()
                        # parameter.add_value_listener(listener)
                        # self.param_listeners.append((parameter, listener))

    def _on_playing_slot_index_changed(self, track, loop_index):
        loop_state = LOOP_STATE.STOPPED
        slot_index = track.playing_slot_index
        if slot_index >= 0:
            #TODO: do we want to verify slot_index matches the loop bank expected?
            loop_state = LOOP_STATE.PLAYING
        self.manager.send_midi_note(0, loop_index, loop_state)

    def _on_portal_name_changed(self):
        portal_name = self.manager.song.return_tracks[self.manager.portal_index].devices[0].chains[0].devices[2].parameters[self.manager.portal_name_index].value_items[0]
        portal_name_bytes = portal_name.encode('ascii', errors='ignore')
        sysex_message = bytes([SYSEX_PREFIX.PORTAL_NAME]) + portal_name_bytes
        self.manager.send_sysex(sysex_message)

    def _on_tide_name_changed(self):
        tide_name = self.manager.song.return_tracks[self.manager.tide_a_index].devices[0].parameters[self.manager.tide_preset_name_index].value_items[0]
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