#--------------------------------------------------------------------------------
# Constants used in AbletonOSC
#--------------------------------------------------------------------------------
from enum import IntEnum

MIDI_TRANSPOSER_DEVICE = "midiTransposer"
OSC_LISTEN_PORT = 11000
OSC_RESPONSE_PORT = 11001
BANK_B_OFFSET = 8
FADE_AMOUNT = 0.05
FADER_ZERO = 0.85
FADER_TIMER_INTERVAL = 0.1667
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

PRESET_INCLUDE_TRACKS = {
    "bass": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": True, "hasChains": False},
    "piano": { "observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": True, "hasChains": False},
    "SYNTH1": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True},
    "SYNTH2": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True},
    "SYNTH3": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True},
    "FOOT": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": True},
    "violin": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "violin2": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "mic": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "vocoder": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": False, "hasChains": False},
    # "vocoderInput": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "looper": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "SuperVPlay": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Sampler": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": False, "hasChains": False},
    "BANKA": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "BANKB": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "BANKaTEMPO": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP1": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP2": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP3": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP4": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP5": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP6": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP7": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP8": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "BANKB": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP9": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP10": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP11": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP12": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP13": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP14": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP15": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "LOOP16": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FOOTLOOPS": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootTempo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop1": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop2": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop3": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop4": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop5": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop6": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop7": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "FootLoop8": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    # "MAX": {"observeVolume": False, "observeMute": False, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadInput1": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadInput2": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadInput3": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadOutput1": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadOutput2": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "IpadOutput3": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "12Step": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "H90Violin": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "H90Vocal": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "12StepFoot": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Korg": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "AkaiBass": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "AkaiKeys": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "TestKeys": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "MergedMidi": {"observeVolume": True, "observeMute": True, "observeSends": False, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "OUTPUTS": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Bass Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Piano Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Violin Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Keys 1 Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Keys 2 Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Keys 3 Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Loops 1 Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Loops 2 Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Foot Loops Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Vocal Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Vocoder Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Tide/FX Stereo": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False}
}

PARAMS_TO_CACHE = {
    MIDI_TRANSPOSER_DEVICE: ["program", "transpose"],
}

CHAINS_TO_IGNORE_TRANSPOSE = [
    "FootLoops"
]

class Channel_1_Note(IntEnum):
    LOOP1 = 0
    LOOP2 = 1
    LOOP3 = 2
    LOOP4 = 3
    LOOP5 = 4
    LOOP6 = 5
    LOOP7 = 6
    LOOP8 = 7
    LOOP9 = 8
    LOOP10 = 9
    LOOP11 = 10
    LOOP12 = 11
    LOOP13 = 12
    LOOP14 = 13
    LOOP15 = 14
    LOOP16 = 15

class Channel_1_CC(IntEnum):
    BANK_A_SELECT = 16
    BANK_B_SELECT = 17
    LOAD_PRESET = 19
    SAVE_PRESET = 20
    LOOP_FADE = 21
    LOOP_FADE_SPEED = 22

class LOOP_VELOCITY(IntEnum):
    STOP_LOOP = 1
    START_LOOP = 2

class LOOP_STATE(IntEnum):
    STOPPED = 3
    PLAYING = 4

class SYSEX_PREFIX(IntEnum):
    LOOP_NAMES = 26


CC_LISTENERS = [
    [Channel_1_CC.BANK_A_SELECT, 0],
    [Channel_1_CC.BANK_B_SELECT, 0],
    [Channel_1_CC.LOAD_PRESET, 0],
    [Channel_1_CC.SAVE_PRESET, 0],
    [Channel_1_CC.LOOP_FADE, 0],
    [Channel_1_CC.LOOP_FADE_SPEED, 0],
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
    NONE = 0
    FADING_IN = 1
    FADING_OUT = 2
    FULL_VOLUME = 3
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