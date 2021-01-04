from enum import Enum
import binascii


def get_bytes(file_object, num_bytes):
    return int.from_bytes(file_object.read(num_bytes), "big")  # SMF are always big-endian


class Format(Enum):
    SINGLE_TRACK = 0
    MULTI_TRACK = 1
    MULTI_SONG = 2


def patch_lookup(patch_number):
    patches = {
        1: "Acoustic Grand Piano",
        2: "Bright Acoustic Piano",
        3: "Electric Grand Piano",
        4: "Honky-tonk Piano",
        5: "Rhodes Piano",
        6: "Chorused Piano",
        7: "Harpsichord",
        8: "Clavinet",
        9: "Celesta",
        10: "Glockenspiel",
        11: "Music Box",
        12: "Vibraphone",
        13: "Marimba",
        14: "Xylophone",
        15: "Tubular Bells",
        16: "Dulcimer",
        17: "Hammond Organ",
        18: "Percussive Organ",
        19: "Rock Organ",
        20: "Church Organ",
        21: "Reed Organ",
        22: "Accordion",
        23: "Harmonica",
        24: "Tango Accordion",
        25: "Acoustic Nylon Guitar",
        26: "Acoustic Steel Guitar",
        27: "Electric Jazz Guitar",
        28: "Electric Clean Guitar",
        29: "Electric Muted Guitar",
        30: "Overdriven Guitar",
        31: "Distortion Guitar",
        32: "Guitar Harmonics",
        33: "Acoustic Bass",
        34: "Fingered Electric Bass",
        35: "Plucked Electric Bass",
        36: "Fretless Bass",
        37: "Slap Bass 1",
        38: "Slap Bass 2",
        39: "Synth Bass 1",
        40: "Synth Bass 2",
        41: "Violin",
        42: "Viola",
        43: "Cello",
        44: "Contrabass",
        45: "Tremolo Strings",
        46: "Pizzicato Strings",
        47: "Orchestral Harp",
        48: "Timpani",
        49: "String Ensemble 1",
        50: "String Ensemble 2",
        51: "Synth Strings 1",
        52: "Synth Strings 2",
        53: "Choir \"Aah\"",
        54: "Choir \"Ooh\"",
        55: "Synth Voice",
        56: "Orchestral Hit",
        57: "Trumpet",
        58: "Trombone",
        59: "Tuba",
        60: "Muted Trumpet",
        61: "French Horn",
        62: "Brass Section",
        63: "Synth Brass 1",
        64: "Synth Brass 2",
        65: "Soprano Sax",
        66: "Alto Sax",
        67: "Tenor Sax",
        68: "Baritone Sax",
        69: "Oboe",
        70: "English Horn",
        71: "Bassoon",
        72: "Clarinet",
        73: "Piccolo",
        74: "Flute",
        75: "Recorder",
        76: "Pan Flute",
        77: "Bottle Blow",
        78: "Shakuhachi",
        79: "Whistle",
        80: "Ocarina",
        81: "Square Wave Lead",
        82: "Sawtooth Wave Lead",
        83: "Calliope Lead",
        84: "Chiff Lead",
        85: "Charang Lead",
        86: "Voice Lead",
        87: "Fifths Lead",
        88: "Bass Lead",
        89: "New Age Pad",
        90: "Warm Pad",
        91: "Polysynth Pad",
        92: "Choir Pad",
        93: "Bowed Pad",
        94: "Metallic Pad",
        95: "Halo Pad",
        96: "Sweep Pad",
        97: "Rain Effect",
        98: "Soundtrack Effect",
        99: "Crystal Effect",
        100: "Atmosphere Effect",
        101: "Brightness Effect",
        102: "Goblins Effect",
        103: "Echoes Effect",
        104: "Sci - Fi Effect",
        105: "Sitar",
        106: "Banjo",
        107: "Shamisen",
        108: "Koto",
        109: "Kalimba",
        110: "Bagpipe",
        111: "Fiddle",
        112: "Shanai",
        113: "Tinkle Bell",
        114: "Agogo",
        115: "Steel Drums",
        116: "Woodblock",
        117: "Taiko Drum",
        118: "Melodic Tom",
        119: "Synth Drum",
        120: "Reverse Cymbal",
        121: "Guitar Fret Noise",
        122: "Breath Noise",
        123: "Seashore",
        124: "Bird Tweet",
        125: "Telephone Ring",
        126: "Helicopter",
        127: "Applause",
        128: "Gun Shot",

    }

    return patches.get(patch_number + 1, "Unknown Patch")


class TrackEvent:
    def __init__(self, v_time, command, data):
        self.v_time = v_time
        self.command = command
        self.data = data
        self.event_type = ""
        self.event_description = ""
        self.populate_event_data()

    def get_nibble(self):
        return self.command[0] >> 4

    def get_channel(self):
        return self.command[0] & 0x0F

    def populate_event_data(self):
        cmd_nib = self.get_nibble()
        chn_nib = self.get_channel()

        # Key Data (May not be used)
        key = get_note_name(self.data[0])
        octave = int(self.data[0] / 12) - 1

        if cmd_nib == 0x8:
            self.event_description = f'{key}{octave}: {self.data[1]}'
            self.event_type = 'Note Off'
            return
        if cmd_nib == 0x9:
            self.event_description = f'{key}{octave}: {self.data[1]}'
            self.event_type = 'Note Off' if self.data[1] == 0 else 'Note On'
            return
        if cmd_nib == 0xA:
            self.event_description = f'{key}{octave}: {self.data[1]}'
            self.event_type = 'Aftertouch'
            return
        if cmd_nib == 0xB:
            self.event_description = f'Controller {self.data[0]}: {self.data[1]}'
            self.event_type = 'Control Change'
            return
        if cmd_nib == 0xC:
            self.event_description = f'Patch {self.data[0] + 1}: {patch_lookup(self.data[0])}'
            self.event_type = 'Patch Change'
            return
        if cmd_nib == 0xD:
            self.event_description = f'{self.data[0] + 1}'
            self.event_type = 'Channel Pressure'
            return
        if cmd_nib == 0xE:
            self.event_description = f'{(self.data[0] & ((1 << 7) - 1)) << 7 | (self.data[1] & ((1 << 7) - 1))}'
            # TODO may be wrong idk or really care right now
            self.event_type = 'Pitch Bend'
            return
        if cmd_nib == 0xF:
            if chn_nib == 0x0 or chn_nib == 0x7:
                self.event_description = self.data[1:].decode().strip()
                self.event_type = 'System Exclusive Message'

            meta_type = self.data[0]
            try:
                self.event_description = self.data[2:].decode('utf-8').strip()
            except UnicodeError:
                self.event_description = "Invalid UTF-8 String"
            if meta_type == 0x00:
                self.event_type = 'Sequence Number'
                return
            if meta_type == 0x01:
                self.event_type = 'Text Event'
                return
            if meta_type == 0x02:
                self.event_type = 'Copyright Notice'
                return
            if meta_type == 0x03:
                self.event_type = 'Sequence/Track Name'
                return
            if meta_type == 0x04:
                self.event_type = 'Instrument Name'
                return
            if meta_type == 0x05:
                self.event_type = 'Lyric Text'
                return
            if meta_type == 0x06:
                self.event_type = 'Marker Text'
                return
            if meta_type == 0x07:
                self.event_type = 'Cue Point'
                return
            if meta_type == 0x20:
                self.event_description = f'Channel: {self.data[2]}'
                self.event_type = 'MIDI Channel Prefix Assignment'
                return
            if meta_type == 0x21:
                self.event_description = f'Port: {self.data[2]}'
                self.event_type = 'MIDI Port Assignment'
                return
            if meta_type == 0x2F:
                self.event_type = 'End of Track'
                return
            if meta_type == 0x51:
                self.event_description = f'Tempo: {self.data[2:]}'
                self.event_type = 'Tempo Setting'
                return
            if meta_type == 0x54:
                self.event_description = f'{self.data[2]}:{self.data[3]}:{self.data[4]}:{self.data[5]}:{self.data[6]}'
                self.event_type = 'SMPTE Offset'
                return
            if meta_type == 0x58:
                self.event_description = f'{self.data[2]} {self.data[3]} {self.data[4]} {self.data[5]}'  # TODO to parse
                self.event_type = 'Time Signature'
                return
            if meta_type == 0x59:
                self.event_description = f'{self.data[2]} {"major" if self.data[3] == 0 else "minor"}'  # TODO parse key
                self.event_type = 'Key Signature'
                return
            if meta_type == 0x7F:
                self.event_type = 'Sequence Specific Event'
                return
            self.event_type = 'Unrecognized Meta Message'
        self.event_type = 'Unsupported Event'
        return

    def __str__(self):
        output_string = f'{self.v_time}\t'
        output_string += f'{str(binascii.hexlify(self.command), "utf-8")} '
        for byte in [bytes([b]) for b in self.data]:
            output_string += f'{str(binascii.hexlify(byte), "utf-8")} '

        event_type = self.event_type
        description = self.event_description
        return f'{output_string}\t{event_type}\t{description}'


def parse_header(midi_file):
    midi_header = get_bytes(midi_file, 4)
    if midi_header != 0x4d546864:
        raise ValueError('Invalid MIDI Header')

    header_length = get_bytes(midi_file, 4)
    if header_length != 6:
        raise ValueError('Invalid header length')

    return get_bytes(midi_file, 2), get_bytes(midi_file, 2), get_bytes(midi_file, 2)


def get_variable_time(midi_file):
    bytes_read = 0
    v_time = 0
    while True:
        byte = get_bytes(midi_file, 1)
        bytes_read += 1

        last_seven = byte & ((1 << 7) - 1)
        v_time = v_time | last_seven

        continuation = bool(byte & (1 << 7))
        if continuation:
            v_time <<= 7
        if not continuation:
            break

    return bytes_read, v_time


def get_note_name(key):
    mod = key % 12
    if mod == 0:
        return "C"
    if mod == 1:
        return "C#"
    if mod == 2:
        return "D"
    if mod == 3:
        return "D#"
    if mod == 4:
        return "E"
    if mod == 5:
        return "F"
    if mod == 6:
        return "F#"
    if mod == 7:
        return "G"
    if mod == 8:
        return "G#"
    if mod == 9:
        return "A"
    if mod == 10:
        return "A#"
    if mod == 11:
        return "B"


def cleaner_event_parse(midi_file):
    bytes_read = 1
    command = midi_file.read(1)
    cmd_nib = command[0] >> 4
    chn_nib = command[0] & 0x0F

    data = bytearray()

    if cmd_nib == 0x8 or cmd_nib == 0x9 or cmd_nib == 0xA or cmd_nib == 0xA or cmd_nib == 0xB or cmd_nib == 0xE:
        data += bytearray(midi_file.read(2))
        bytes_read += 2
    elif cmd_nib == 0xC or cmd_nib == 0xD:
        data += bytearray(midi_file.read(1))
        bytes_read += 1
    elif cmd_nib == 0xF:
        if chn_nib == 0xF:
            meta_type = midi_file.read(1)
            meta_length = midi_file.read(1)
            meta_data = midi_file.read(meta_length[0])
            data += bytearray(meta_type) + bytearray(meta_length) + bytearray(meta_data)
            bytes_read += meta_length[0] + 2
        elif chn_nib == 0x0 or chn_nib == 0x7:
            sysex = midi_file.read(1)
            bytes_read += 1
            while sysex != 0xF7:
                data += bytearray(sysex)
                sysex = midi_file.read(1)
                bytes_read += 1
        else:
            raise ValueError('Bad command.')
    else:
        raise ValueError('Bad command.')  # TODO add byte number

    return bytes_read, command, data


def get_track_event(midi_file):
    v_time_length, v_time = get_variable_time(midi_file)
    event_length, command, data = cleaner_event_parse(midi_file)

    return v_time_length + event_length, TrackEvent(v_time, command, data)


def parse_track(midi_file, delta):
    track_header = get_bytes(midi_file, 4)
    if track_header != 0x4d54726b:
        raise ValueError('Invalid Track header')

    track_length = get_bytes(midi_file, 4)
    track_events = []
    bytes_processed = 0
    while bytes_processed < track_length:
        track_event_length, track_event = get_track_event(midi_file)
        bytes_processed += track_event_length
        track_events.append(track_event)
    return track_events


with open('Twinkle.mid', 'rb') as f:
    midi_format, num_track_chunks, division = parse_header(midi_file=f)

    if midi_format == Format.MULTI_SONG:
        raise ValueError('Multi song midi not yet supported')
    if midi_format > 2:
        raise ValueError('Invalid midi format')
    if bool(division & (1 << 15)):
        raise ValueError('SMPTE Time Code not yet supported')

    tracks = [parse_track(midi_file=f, delta=division) for track in range(num_track_chunks)]

    for track in tracks:
        track_print_data = [['Delta Time', 'MIDI Message', 'Event Type', 'Description of Event']]
        for event in track:
            event_string = str(event)
            track_print_data.append(event_string.split('\t'))

        col_widths = []
        for col in range(len(track_print_data[0])):
            current_column_max = 0
            for row in range(len(track_print_data)):
                current_column_max = max(len(track_print_data[row][col]), current_column_max)
            col_widths.append(current_column_max + 2)

        for i, row in enumerate(track_print_data):
            output = ""
            for j, word in enumerate(row):
                output += "".join(word.ljust(col_widths[j]))
            print(output)
            if i == 0:
                spacer = ""
                for width in col_widths:
                    spacer += "=" * width
                print(spacer)
        print('\n')
