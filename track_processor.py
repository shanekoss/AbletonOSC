from typing import Tuple, Any, Callable, Optional, List
from .abletonosc.constants import LOOPTRACK_NAMES, BANK_A_TEMPO, BANK_B_OFFSET

import Live # type: ignore
import logging

class TrackProcessor():
    def __init__(self):
        self.class_identifier = "track_processor"
        self.loop_tracks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.manager = None
        self.logger = None
        self.bankATempoIndex = -1
        self.currentBankAIndex = -1
        self.currentBankBIndex = -1
        self.track_listeners = []
    def processTracks(self, tracks: List[Live.Track.Track]):
        self.logger.info("PROCESSING THE FUCKING TRACKS!")
        for index, track in enumerate(tracks):
            self.logger.info(f"FOUND TRACK {track.name} with index: {index}")
            if track.name == BANK_A_TEMPO:
                self.logger.info(f"bankATempoIndex index is {index}!")
                self.bankATempoIndex = index
                continue
            if track.name in LOOPTRACK_NAMES:
                loop_index = LOOPTRACK_NAMES.index(track.name)
                if loop_index != -1:
                    if loop_index >= len(self.loop_tracks):
                        self.logger.error(f"Loop Index ${loop_index} is out of range! BAD!")
                    else:
                        self.logger.info(f"LOOPTRACK {loop_index} is {track.name}")
                        self.loop_tracks[loop_index] = index
                        listener = lambda t=track, l=loop_index: self._on_playing_slot_index_changed(t, l)
                        track.add_playing_slot_index_listener(listener)
                        self.track_listeners.append((track, listener))  # Store for cleanup
                    continue

    def _on_playing_slot_index_changed(self, track, loop_index):
        loop_state = 3
        slot_index = track.playing_slot_index
        if slot_index >= 0:
            #TODO: do we want to verify slot_index matches the loop bank expected?
            loop_state = 4
        self.manager.send_midi_note(0, loop_index, loop_state)

    def sendBankANames(self, bank_a_index):
        for index, track_index in enumerate(self.loop_tracks[:8]):
            clip_name =" "
            if self.manager.song.tracks[track_index].clip_slots[bank_a_index].clip != None:
                clip_name = self.manager.song.tracks[track_index].clip_slots[bank_a_index].clip.name
            clip_name_bytes = clip_name.encode('ascii', errors='ignore')
            sysex_message = bytes([26, index]) + clip_name_bytes
            self.manager.send_sysex(sysex_message)
    def sendBankBNames(self, bank_b_index):
        for index, track_index in enumerate(self.loop_tracks[8:]):
            clip_name =" "

            if bank_b_index < len(self.manager.song.tracks[track_index].clip_slots) and self.manager.song.tracks[track_index].clip_slots[bank_b_index].clip != None:
                clip_name = self.manager.song.tracks[track_index].clip_slots[bank_b_index].clip.name
            clip_name_bytes = clip_name.encode('ascii', errors='ignore')
            sysex_message = bytes([26, index + BANK_B_OFFSET]) + clip_name_bytes
            self.manager.send_sysex(sysex_message)

    def disconnect(self):
        """Remove all listeners on script shutdown"""
        for track, listener in self.track_listeners:
            if track.playing_slot_index_has_listener(listener):
                track.remove_playing_slot_index_listener(listener)
        self.track_listeners = []  # Clear the list