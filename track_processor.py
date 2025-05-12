from typing import Tuple, Any, Callable, Optional, List
from .abletonosc.constants import LOOPTRACK_NAMES, BANK_A_TEMPO

import Live
import logging

class TrackProcessor():
    def __init__(self):
        self.class_identifier = "track_processor"
        self.loop_tracks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.manager = None
        self.logger = None
        self.bankATempoIndex = -1
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
                    continue
        # set up bank a fired index listener:
        if self.bankATempoIndex != -1:
            new_array_with_bank_index = [self.bankATempoIndex] + self.loop_tracks[:8]
            self.logger.info(f"setting up damn handler with {new_array_with_bank_index}")
            self.manager.get_handler_by_identifier("track").create_track_callback_for_loop_fired_index(new_array_with_bank_index)
                    