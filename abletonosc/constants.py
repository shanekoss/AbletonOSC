#--------------------------------------------------------------------------------
# Constants used in AbletonOSC
#--------------------------------------------------------------------------------

MIDI_TRANSPOSER_DEVICE = "midiTransposer_p"
OSC_LISTEN_PORT = 11000
OSC_RESPONSE_PORT = 11001
BANK_B_OFFSET = 8

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
    "FOOT": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": True, "hasChains": False},
    "violin": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "violin2": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "mic": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "vocoder": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": False, "hasChains": False},
    # "vocoderInput": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "looper": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "SuperVPlay": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
    "Sampler": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": True, "hasTransp": False, "hasChains": False},
    "BANKA": {"observeVolume": True, "observeMute": True, "observeSends": True, "hasPGM": False, "hasTransp": False, "hasChains": False},
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

CC_LISTENERS = [
    [16, 0], #BANK A LOOP SELECT
    [17, 0], #BANK B LOOP SELECT
    [19, 0], #LOAD PRESET
    [20, 0], #SAVE PRESET
]

NOTE_LISTENERS = [
    [0, 0], #LOOPA TRIGGER 1
    [1, 0], #LOOPA TRIGGER 2
    [2, 0], #LOOPA TRIGGER 3
    [3, 0], #LOOPA TRIGGER 4
    [4, 0], #LOOPA TRIGGER 5
    [5, 0], #LOOPA TRIGGER 6
    [6, 0], #LOOPA TRIGGER 7
    [7, 0], #LOOPA TRIGGER 8
    [8, 0], #LOOPB TRIGGER 1
    [9, 0], #LOOPB TRIGGER 2
    [10, 0], #LOOPB TRIGGER 3
    [11, 0], #LOOPB TRIGGER 4
    [12, 0], #LOOPB TRIGGER 5
    [13, 0], #LOOPB TRIGGER 6
    [14, 0], #LOOPB TRIGGER 7
    [15, 0]  #LOOPB TRIGGER 8
]

PARAMS_TO_CACHE = {
    MIDI_TRANSPOSER_DEVICE: ["program", "transpose"],
}
