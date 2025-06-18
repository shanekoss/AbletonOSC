#--------------------------------------------------------------------------------
# Constants used in AbletonOSC
#--------------------------------------------------------------------------------
from enum import IntEnum
from enum import Enum

MIDI_TRANSPOSER_DEVICE = "midiTransposer"
OSC_LISTEN_PORT = 11000
OSC_RESPONSE_PORT = 11001
BANK_B_OFFSET = 8
FADE_AMOUNT = 0.05
FADER_ZERO = 0.85
BANK_A_TEMPO = "BANKaTEMPO"
LOOPTRACK_NAMES = [
    "LOOP1",
    "LOOP2",
    "LOOP3",
    "LOOP4",
    "LOOP5",
    "LOOP6",
    "LOOP7",
    "LOOP8",
    "LOOP9",
    "LOOP10",
    "LOOP11",
    "LOOP12",
    "LOOP13",
    "LOOP14",
    "LOOP15",
    "LOOP16"
]

PARAMS_TO_CACHE = {
    MIDI_TRANSPOSER_DEVICE: ["program", "transpose"],
}

CHAINS_TO_IGNORE_TRANSPOSE = [
    "FootLoops"
]

class RME_SPLITS(IntEnum):
    STEREO = 0,
    LOOPS = 1,
    KEYS = 2,
    VOCAL = 3,
    BASS = 4

class DANTE_SPLITS(IntEnum):
    BASS_STEREO = 0,
    PIANO_STEREO = 1,
    VIOLIN_STEREO = 2,
    KEYS1_STEREO = 3,
    KEYS2_STEREO = 4,
    KEYS3_STEREO = 5,
    LOOPS1_STEREO = 6,
    LOOPS2_STEREO = 7,
    FOOT_LOOPS_STEREO = 8,
    VOCAL_STEREO = 9,
    VOCODER_STEREO = 10,
    TIDE_FX_STEREO = 11,

class Channel_1_Note(IntEnum):
    LOOP1 = 0,
    LOOP2 = 1,
    LOOP3 = 2,
    LOOP4 = 3,
    LOOP5 = 4,
    LOOP6 = 5,
    LOOP7 = 6,
    LOOP8 = 7,
    LOOP9 = 8,
    LOOP10 = 9,
    LOOP11 = 10,
    LOOP12 = 11,
    LOOP13 = 12,
    LOOP14 = 13,
    LOOP15 = 14,
    LOOP16 = 15,

class STATE(IntEnum):
    SPLITS = 1

class ROUTING(IntEnum):
    STEREO = 0,
    RME = 1,
    RME_OPTICAL = 2
    DANTE = 3

class Channel_1_CC(IntEnum):
    BANK_A_SELECT = 16,
    BANK_B_SELECT = 17,
    LOAD_PRESET = 19,
    SAVE_PRESET = 20,
    LOOP_FADE = 21,
    LOOP_FADE_SPEED = 22

class LOOP_VELOCITY(IntEnum):
    STOP_LOOP = 1,
    START_LOOP = 2

class LOOP_STATE(IntEnum):
    STOPPED = 3,
    PLAYING = 4

class SYSEX_PREFIX(IntEnum):
    LOOP_NAMES = 26,
    TIDE_NAME = 23,
    PORTAL_NAME = 24

CC_LISTENERS = [
    [Channel_1_CC.BANK_A_SELECT, 0],
    [Channel_1_CC.BANK_B_SELECT, 0],
    [Channel_1_CC.LOAD_PRESET, 0],
    [Channel_1_CC.SAVE_PRESET, 0],
    [Channel_1_CC.LOOP_FADE, 0],
    [Channel_1_CC.LOOP_FADE_SPEED, 0]
]

NOTE_LISTENERS = [
    [Channel_1_Note.LOOP1, 0],
    [Channel_1_Note.LOOP2, 0],
    [Channel_1_Note.LOOP3, 0],
    [Channel_1_Note.LOOP4, 0],
    [Channel_1_Note.LOOP5, 0],
    [Channel_1_Note.LOOP6, 0],
    [Channel_1_Note.LOOP7, 0],
    [Channel_1_Note.LOOP8, 0],
    [Channel_1_Note.LOOP9, 0],
    [Channel_1_Note.LOOP10, 0],
    [Channel_1_Note.LOOP11, 0],
    [Channel_1_Note.LOOP12, 0],
    [Channel_1_Note.LOOP13, 0],
    [Channel_1_Note.LOOP14, 0],
    [Channel_1_Note.LOOP15, 0],
    [Channel_1_Note.LOOP16, 0] 
]

class LOOP_FADE_STATE(IntEnum): 
    NONE = 0,
    FADING_IN = 1,
    FADING_OUT = 2,
    FULL_VOLUME = 3,
    VOLUME_ALL_DOWN = 4

LOOP_FADE_STATES = {
    "LOOP1": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP2": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP3": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP4": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP5": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP6": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP7": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP8": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP9": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP10": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP11": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP12": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP13": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP14": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP15": {"state" : LOOP_FADE_STATE.NONE},
    "LOOP16": {"state" : LOOP_FADE_STATE.NONE},
}

class RETURNS(str, Enum):
    TIDE = 'A-TIDEa'
    PORTAL ='B-PORTAL'
    LOOPER = 'C-toLOOPER'
    STEREO = 'D-STEREO'
    LOOPS = 'E-LOOPS'
    KEYS = 'F-KEYS'
    VOCAL = 'G-VOCAL'
    BASS = 'H-BASS'
    INSTA_SAMPLER = 'I-to INSTA'

RETURN_TRACKS = {
    RETURNS.TIDE: {"index": -1},
    RETURNS.PORTAL: {"index": -1},
    RETURNS.LOOPER: {"index": -1},
    RETURNS.STEREO: {"index": -1},
    RETURNS.LOOPS: {"index": -1},
    RETURNS.KEYS: {"index": -1},
    RETURNS.VOCAL: {"index": -1},
    RETURNS.BASS: {"index": -1},
    RETURNS.INSTA_SAMPLER: {"index": -1}
}

PRESET_INCLUDE_TRACKS = {
    "bass": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": True, "hasChains": False, "rme": RME_SPLITS.BASS, "dante": DANTE_SPLITS.BASS_STEREO},
    "piano": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": True, "hasChains": False, "rme": RME_SPLITS.KEYS, "dante": DANTE_SPLITS.PIANO_STEREO},
    "SYNTH1": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True, "rme": RME_SPLITS.KEYS, "dante": DANTE_SPLITS.KEYS1_STEREO},
    "SYNTH2": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True, "rme": RME_SPLITS.KEYS, "dante": DANTE_SPLITS.KEYS2_STEREO},
    "SYNTH3": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True, "rme": RME_SPLITS.KEYS, "dante": DANTE_SPLITS.KEYS2_STEREO},
    "FOOT": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True, "rme": RME_SPLITS.LOOPS, "dante": DANTE_SPLITS.FOOT_LOOPS_STEREO},
    "violin": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False, "rme": RME_SPLITS.KEYS, "dante": DANTE_SPLITS.KEYS2_STEREO},
    "violin2": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "mic": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "vocoder": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": False, "hasChains": False},
    # "vocoderInput": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "looper": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "SuperVPlay": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Sampler": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": False},
    "BANKA": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "BANKaTEMPO": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP1": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP2": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP3": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP4": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP5": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP6": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP7": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP8": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "BANKB": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP9": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP10": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP11": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP12": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP13": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP14": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP15": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP16": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FOOTLOOPS": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootTempo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop1": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop2": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop3": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop4": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop5": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop6": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop7": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop8": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "STATE": {"index": -1, "observeVolume": False, "observeMute": False, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadInput1": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadInput2": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadInput3": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadOutput1": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadOutput2": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadOutput3": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "12Step": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "H90Violin": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "H90Vocal": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "12StepFoot": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Korg": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "AkaiBass": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "AkaiKeys": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "TestKeys": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "MergedMidi": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "OUTPUTS": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Bass Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Piano Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Violin Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Keys 1 Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Keys 2 Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Keys 3 Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Loops 1 Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Loops 2 Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Foot Loops Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Vocal Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Vocoder Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Tide/FX Stereo": {"index": -1, "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False}
}