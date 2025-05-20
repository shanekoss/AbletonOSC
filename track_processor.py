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
    def processTracks(self, tracks: List[Live.Track.Track]):
        for index, track in enumerate(tracks):
            if track.name == BANK_A_TEMPO:
                self.manager.bankATempoIndex = index
                continue
            if track.name in LOOPTRACK_NAMES:
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

    def _on_playing_slot_index_changed(self, track, loop_index):
        loop_state = LOOP_STATE.STOPPED
        slot_index = track.playing_slot_index
        if slot_index >= 0:
            #TODO: do we want to verify slot_index matches the loop bank expected?
            loop_state = LOOP_STATE.PLAYING
        self.manager.send_midi_note(0, loop_index, loop_state)

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