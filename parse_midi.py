import math
from enum import Enum
import binascii
from fractions import Fraction


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


def key_lookup(key, mode):
    if mode != 0 and mode != 1:
        raise ValueError('Invalid mode')

    keys = {
        -7: ["Cb Major", "Ab Minor"],
        -6: ["Gb Major", "Eb Minor"],
        -5: ["Db Major", "Bb Minor"],
        -4: ["Ab Major", "F Minor"],
        -3: ["Eb Major", "C Minor"],
        -2: ["Bb Major", "G Minor"],
        -1: ["F Major", "D Minor"],
        0: ["C Major", "A Minor"],
        1: ["G Major", "E Minor"],
        2: ["D Major", "B Minor"],
        3: ["A Major", "F# Minor"],
        4: ["E Major", "C# Minor"],
        5: ["B Major", "G# Minor"],
        6: ["F# Major", "D# Minor"],
        7: ["C# Major", "A# Minor"],
    }

    return keys.get(key, ["Unknown", "Unknown"])[mode]


def pprint_table(table_data):
    string_output = ""
    col_widths = []

    for col in range(len(table_data[0])):
        current_column_max = 0
        for row in range(len(table_data)):
            current_column_max = max(len(table_data[row][col]), current_column_max)
        col_widths.append(current_column_max + 2)

    for i, row in enumerate(table_data):
        output = ""
        for j, word in enumerate(row):
            output += "".join(word.ljust(col_widths[j]))
        string_output += output + "\n"

        if i == 0:
            spacer = ""
            for width in col_widths:
                spacer += "=" * width
            string_output += spacer + "\n"

    return string_output


class Track:
    def __init__(self, events, track_id):
        self.events = events
        self.id = track_id
        self.label_events()

    def __str__(self):
        track_print_data = [['Delta Time', 'MIDI Message', 'Event Type', 'Description of Event']]
        for event in self.events:
            event_string = str(event)
            track_print_data.append(event_string.split('\t'))

        string_output = pprint_table(track_print_data)
        return string_output

    def label_events(self):
        for event in self.events:
            event.track_id = self.id


class TrackEvent:
    def __init__(self, tick, command, data):
        self.tick = tick
        self.command = command
        self.data = data
        self.event_type = ""
        self.event_description = ""
        self.populate_event_data()
        self.track_id = -1

    def get_nibble(self):
        return self.command[0] >> 4

    def get_channel(self):
        return self.command[0] & 0x0F

    def populate_event_data(self):
        cmd_nib = self.get_nibble()
        chn_nib = self.get_channel()

        # Key Data (May not be used)
        key = 0
        octave = 0
        perc = chn_nib == 0x9

        if len(self.data) > 0:
            key = get_note_name(self.data[0])
            octave = int(self.data[0] / 12) - 1

        if cmd_nib == 0x8:
            self.event_description = f'{key}{octave}: {self.data[1]}'
            self.event_type = 'Note Off'
            return
        if cmd_nib == 0x9:
            self.event_description = f'{key}{octave}{"*" if perc else ""}: {self.data[1]}'
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
                return

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
                self.event_description = f'{self.data[2]}/{2 ** self.data[3]} '
                self.event_description += f'({self.data[4]} ticks per click, '
                self.event_description += f'{self.data[5]} 32nd-notes per quarter note)'
                self.event_type = 'Time Signature'
                return
            if meta_type == 0x59:
                self.event_description = f'{key_lookup(self.data[2], self.data[3])}'
                self.event_type = 'Key Signature'
                return
            if meta_type == 0x7F:
                self.event_type = 'Sequence Specific Event'
                return
            self.event_type = 'Unrecognized Meta Message'
        self.event_type = 'Unsupported Event'
        return

    def __str__(self):
        output_string = f'{self.tick}\t'
        output_string += f'{str(binascii.hexlify(self.command), "utf-8")} '
        for byte in [bytes([b]) for b in self.data]:
            output_string += f'{str(binascii.hexlify(byte), "utf-8")} '

        event_type = self.event_type
        description = self.event_description
        return f'{output_string}\t{event_type}\t{description}'


def parse_header(midi_file):
    midi_header = midi_file.read(4)
    if midi_header != b'MThd':
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
            sysex_bytes = midi_file.read(1)[0]
            bytes_read += 1
            midi_file.read(sysex_bytes)
            bytes_read += sysex_bytes
        else:
            raise ValueError('Bad command.')
    else:
        # TODO Implement Running Status
        #   This is 2AM me talking but I was running into a parsing issue with a midi file downloaded from the internet.
        #   It took me forever to figure out but I discovered the issue was that of the MIDI "running status", which
        #   was only briefly mentioned in the original spec I was using to implement this. However it's a big deal
        #   when it comes to processing MIDI events specifically. Here's how I think it works:
        #
        #   Every time we receive an event, we set the running status to be the command byte. However, if the command
        #   seemingly doesn't exist, we know to use the previous command (or the last command to set the running status)
        #   as the command for this event, and proceed as if we had read the running status as the command.
        #
        #   This works because all valid track event commands are 1 high i.e, greater than 0x80, and every MIDI command
        #   value is AT MOST 127 or 0x7F, so we can safely chain together identically status-ed MIDI events without
        #   worry.
        #
        #   System/meta events do not use running status and clear it. Do not make the mistake of setting the running
        #   status to 0xFF, because then if there really is an invalid command, it will be read as a system event which
        #   could corrupt the file completely. If this is the case, then we have a bad command, and should handle it
        #   somewhat gracefully.

        raise ValueError('Bad command.')  # TODO add byte number

    return bytes_read, command, data


def get_track_event(midi_file):
    v_time_length, v_time = get_variable_time(midi_file)
    event_length, command, data = cleaner_event_parse(midi_file)

    return v_time_length + event_length, TrackEvent(v_time, command, data)


def parse_track(midi_file):
    track_header = midi_file.read(4)
    if track_header != b'MTrk':
        raise ValueError('Invalid Track header')

    track_length = get_bytes(midi_file, 4)
    track_events = []
    bytes_processed = 0
    while bytes_processed < track_length:
        track_event_length, track_event = get_track_event(midi_file)
        bytes_processed += track_event_length
        track_events.append(track_event)
        print(track_event)
    return track_events


def create_song():
    with open('snowman.mid', 'rb') as f:
        midi_format, num_track_chunks, division = parse_header(midi_file=f)

        if midi_format == Format.MULTI_SONG:
            raise ValueError('Multi song midi not yet supported')
        if midi_format > 2:
            raise ValueError('Invalid midi format')
        if bool(division & (1 << 15)):
            raise ValueError('SMPTE Time Code not yet supported')

        tracks = [Track(parse_track(midi_file=f), i) for i in range(num_track_chunks)]

        for track in tracks:
            print(track)

        # new_song = Song(tracks, division)
        # print(new_song)


def get_perc_sound(key):
    perc_lookup = {
        35: "Acoustic Bass Drum",
        36: "Bass Drum 1",
        37: "Side Stick",
        38: "Acoustic Snare",
        39: "Hand Clap",
        40: "Electric Snare",
        41: "Low Floor Tom",
        42: "Closed High Hat",
        43: "High Floor Tom",
        44: "Pedal High Hat",
        45: "Low Tom",
        46: "Open High Hat",
        47: "Low Mid Tom",
        48: "High Mid Tom",
        49: "Crash Cymbal 1",
        50: "High Tom",
        51: "Ride Cymbal 1",
        52: "Chinese Cymbal",
        53: "Ride Bell",
        54: "Tambourine",
        55: "Splash Cymbal",
        56: "Cowbell",
        57: "Crash Cymbal 2",
        58: "Vibraslap",
        59: "Ride Cymbal 2",
        60: "High Bongo",
        61: "Low Bongo",
        62: "Mute High Conga",
        63: "Open High Conga",
        64: "Low Conga",
        65: "High Timbale",
        66: "Low Timbale",
        67: "High Agogo",
        68: "Low Agogo",
        69: "Cabasa",
        70: "Maracas",
        71: "Short Whistle",
        72: "Long Whistle",
        73: "Short Guiro",
        74: "Long Guiro",
        75: "Claves",
        76: "High Wood Block",
        77: "Low Wood Block",
        78: "Mute Cuica",
        79: "Open Cuica",
        80: "Mute Triangle",
        81: "Open Triangle",
    }

    return perc_lookup.get(key, "Unknown Percussion")


class Note:
    def __init__(self, start_tick, channel, key, vel):
        self.start_tick = start_tick
        self.end_tick = start_tick
        self.channel = channel
        self.perc = channel == 0x9
        self.key = key
        self.velocity = vel
        self.perc_sound = get_perc_sound(key) if self.perc else ""
        self.note_name = f'{get_note_name(key)}{int(key / 12) - 1}'


def create_chord_vector(combined_octaves):
    NOTES_IN_OCTAVE = 12
    chord_vector = [0 for _ in range(NOTES_IN_OCTAVE)]
    note_lookup = {
        "C": 0,
        "C#": 1,
        "D": 2,
        "D#": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "G": 7,
        "G#": 8,
        "A": 9,
        "A#": 10,
        "B": 11
    }

    for note in combined_octaves:
        chord_vector[note_lookup.get(note)] = combined_octaves[note]

    return chord_vector


def parse_chord(actual_notes):
    # Weight each note based on its presence (length)
    weight_sum = sum(note.end_tick - note.start_tick for note in actual_notes)
    # TODO these modifiers aren't really good because they can't easily be set to have no effect
    VELOCITY_MOD = 0.25  # How much should velocity affect the weight of a note?
    ROOT_MOD = 2  # How much should being root note affect the weight of a note?
    weighted_notes = sorted([
        {
            'note': note,
            'weight': ((note.end_tick - note.start_tick) / weight_sum) *
                      (VELOCITY_MOD * note.velocity) *
                      (ROOT_MOD if i == 0 else 1)
        } for i, note in enumerate(actual_notes)
    ], key=lambda n: n['weight'], reverse=True)

    # Merge octaves by combining weights
    combined_octaves = {}
    for note in weighted_notes:
        note_name = get_note_name(note['note'].key)
        if note_name not in combined_octaves:
            combined_octaves[note_name] = 0
        combined_octaves[note_name] += note['weight']

    # Normalize Chord Weights
    weight_sum = sum(combined_octaves[note] for note in combined_octaves)
    for note in combined_octaves:
        combined_octaves[note] /= weight_sum

    chord_vector = create_chord_vector(combined_octaves)
    closest_chords = match_chord_vector(chord_vector)

    output = ", ".join(chord.name for chord in closest_chords)
    return output


class Song:
    def __init__(self, tracks, division):
        self.tracks = tracks
        self.division = division
        self.event_stream = self.make_event_stream()
        self.notes = self.parse_notes()
        self.channels = self.get_channels()
        self.length = self.get_length()

    def parse_notes(self):
        notes = []

        notes_on = []  # TODO could be hashed but I can't be bothered

        ticks = sorted(self.event_stream.keys())

        for tick in ticks:
            events = self.event_stream[tick]
            for event in events:
                channel = event.get_channel()
                key = event.data[0]

                if event.event_type == "Note On":
                    vel = event.data[1]
                    notes_on.append(Note(tick, channel, key, vel))

                if event.event_type == "Note Off":
                    for note in notes_on:
                        if note.channel == channel and note.key == key:
                            note.end_tick = tick
                            notes.append(note)
                            notes_on.remove(note)

        return sorted(notes, key=lambda n: n.start_tick)

    def get_channels(self):
        channels = set()
        ticks = sorted(self.event_stream.keys())

        for tick in ticks:
            events = self.event_stream[tick]
            for event in events:
                if event.get_nibble() != 0xF:
                    channels.add(event.get_channel())
        return list(channels)

    def get_notes_in_range(self, start_tick, end_tick):
        in_range = []
        if start_tick > end_tick:
            return in_range

        for note in self.notes:
            start = note.start_tick
            end = note.end_tick

            if end > start_tick and start <= end_tick:
                in_range.append(note)

        return in_range

    def make_event_stream(self):
        event_stream = {}
        for track in self.tracks:
            current_tick = 0
            for event in track.events:
                tick = event.tick + current_tick
                if tick not in event_stream:
                    event_stream[tick] = []
                event_stream[tick].append(event)
                current_tick = tick
        return event_stream

    def get_event_stream_printout(self):
        song_data = [['Tick', 'Measure', 'Beat']]
        HEADER_DATA = len(song_data[0])
        for track in self.tracks:
            song_data[0].append(f'Track {track.id}')

        ticks = sorted(self.event_stream.keys())

        for tick in ticks:
            events = [['' for _ in song_data[0]]]
            events[0][0] = str(tick)
            events[0][1] = str(self.get_measure(tick))
            events[0][2] = str(self.get_beat(tick))

            for event in self.event_stream[tick]:
                event_list = 0

                while events[event_list][event.track_id + HEADER_DATA] != '':
                    event_list += 1
                    if event_list >= len(events):
                        events.append(['' for _ in song_data[0]])

                events[event_list][event.track_id + HEADER_DATA] += f'{event.event_type} {event.event_description}'

            for event_list in events:
                song_data.append(event_list)

        return pprint_table(song_data)

    def get_measure(self, tick):
        # TODO account for different time signatures
        time_signature_numerator = 4
        return int(tick / (self.division * time_signature_numerator)) + 1

    def get_beat(self, tick):
        # TODO account for different time signatures
        time_signature_numerator = 4
        beat_number = int((tick % (self.division * time_signature_numerator)) / self.division) + 1
        beat_fraction = Fraction(
            (tick % (self.division * time_signature_numerator)) / self.division + 1).limit_denominator() - beat_number
        return f'{beat_number} {beat_fraction}'

    def __str__(self):
        song_data = [['Tick', 'Measure', 'Beat', 'Notes', 'Chord']]
        HEADER_DATA = len(song_data[0])
        for channel in self.channels:
            song_data[0].append(f'Channel {channel + 1}')

        current_tick = 0
        beat_size = self.division  # TODO account for different time signatures
        while current_tick < (self.length + beat_size):
            beat = ['' for _ in song_data[0]]
            notes = self.get_notes_in_range(current_tick, current_tick + beat_size - 1)
            beat[0] = str(int(current_tick))
            beat[1] = str(self.get_measure(current_tick))
            beat[2] = str(self.get_beat(current_tick))

            actual_notes = [n for n in sorted(notes, key=lambda x: x.key) if n.channel != 0x9]

            for note in notes:
                note_name = f'{note.note_name} '
                channel_index = self.channels.index(note.channel) + HEADER_DATA
                if note_name not in beat[channel_index]:
                    beat[channel_index] += note_name

            for note in actual_notes:
                note_name = f'{note.note_name} '
                if note_name not in beat[3]:
                    beat[3] += note_name

            beat[4] = parse_chord(actual_notes)
            current_tick += beat_size
            song_data.append(beat)

        return pprint_table(song_data)

    def get_length(self):
        ticks = sorted(self.event_stream.keys(), reverse=True)
        return ticks[0]


class Chord:
    def __init__(self, vector, name):
        # TODO consider alternate chord names?
        self.vector = vector + [0] * (12 - len(vector))
        self.name = name

    def distance(self, other):
        return math.sqrt(sum((self.vector[i] - other.vector[i]) ** 2 for i in range(12)))


def match_chord_vector(chord_vector):
    # TODO consider key signature?
    input_chord = Chord(chord_vector, "Unnamed")

    # TODO create generator for this library
    chord_library = generate_chord_library()
    # chord_library = [
    #     Chord([0.4, 0, 0, 0, 0.3, 0, 0, 0.3, 0, 0, 0, 0], "C"),
    #     Chord([0, 0, 0.4, 0, 0, 0, 0.3, 0, 0, 0.3, 0, 0], "D"),
    #     Chord([0, 0, 0, 0, 0.4, 0, 0, 0, 0.3, 0, 0, 0.3], "E"),
    #     Chord([0.6, 0, 0, 0, 0, 0, 0, 0.4, 0, 0, 0, 0], "C5"),
    # ]

    # Compute distance to each chord in library
    distances = [[input_chord.distance(chord), chord] for chord in chord_library]
    distances = sorted(distances, key=lambda chord: chord[0])

    DISTANCE_THRESHOLD = 0.5
    close_chords = [chord[1] for chord in distances if chord[0] <= DISTANCE_THRESHOLD]

    return close_chords


def generate_chord_library():
    library = []

    # Multiplier for the weight of the root note,
    # will be semi-normalized so it will become less potent as you add notes to the chord
    ROOT_MOD = 1.5

    chord_templates = [
        [[0, 7], "5"],
        [[0, 4, 7], ""],
        [[0, 3, 7], "m"],
        [[0, 4, 8], "+"],
        [[0, 2, 7], "sus2"],
        [[0, 5, 7], "sus"],
        [[0, 4, 7, 9], "6"],
        [[0, 4, 7, 10], "7"],
        [[0, 4, 7, 11], "maj7"],
        [[0, 3, 7, 10], "m7"],
        [[0, 4, 7, 14], "add9"],
    ]

    for template in chord_templates:
        steps = template[0]
        name = template[1]
        for i in range(12):
            new_chord = Chord([], f'{get_note_name(i)}{name}')
            for step in steps:
                idx = (i + step) % 12
                new_chord.vector[idx] = 1 / len(steps)
                if step == 0:
                    new_chord.vector[idx] *= ROOT_MOD

            # "Normalize"
            new_chord.vector = [x / sum(new_chord.vector) for x in new_chord.vector]
            library.append(new_chord)
    return library


if __name__ == "__main__":
    create_song()
