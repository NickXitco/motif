from enum import Enum


def get_bytes(file_object, num_bytes):
    return int.from_bytes(file_object.read(num_bytes), "big")  # SMF are always big-endian


class Format(Enum):
    SINGLE_TRACK = 0
    MULTI_TRACK = 1
    MULTI_SONG = 2


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
        v_time <<= 7

        continuation = bool(byte & (1 << 7))
        if not continuation:
            break

    return bytes_read, v_time


def parse_system_event(midi_file, kind):
    bytes_read = 0
    if kind == 0xF:
        # Meta Event
        meta_type = get_bytes(midi_file, 1)
        meta_length = get_bytes(midi_file, 1)
        event_data = get_bytes(midi_file, meta_length)
        bytes_read += meta_length + 2
    elif kind == 0x0 or kind == 0x7:
        # Sysex Event
        sysex = get_bytes(midi_file, 1)
        bytes_read += 1
        while sysex != 0xF7:
            sysex = get_bytes(midi_file, 1)
            bytes_read += 1
    else:
        raise ValueError('Bad System Event')

    return bytes_read, None


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


def parse_event(midi_file):
    bytes_read = 0
    command_byte = get_bytes(midi_file, 1)
    if command_byte < 128:
        raise ValueError('Invalid MIDI command')

    command_nibble = command_byte >> 4
    channel_nibble = command_byte & 0x0F  # Probably don't need this part

    bytes_read += 1
    if command_nibble == 0x8:
        # Note off
        print('Note Off')
        key = get_bytes(midi_file, 1)
        release_velocity = get_bytes(midi_file, 1)
        bytes_read += 2
    if command_nibble == 0x9:
        # Note on
        key = get_bytes(midi_file, 1)
        octave = int(key / 12) - 1
        letter = get_note_name(key)
        attack_velocity = get_bytes(midi_file, 1)
        print(f'Note On {letter}{octave} {attack_velocity}')
        bytes_read += 2
    if command_nibble == 0xA:
        # After-touch
        print('After Touch')
        key = get_bytes(midi_file, 1)
        pressure = get_bytes(midi_file, 1)
        bytes_read += 2
    if command_nibble == 0xB:
        # Control Change
        print('Control Change')
        controller = get_bytes(midi_file, 1)
        controller_data = get_bytes(midi_file, 1)
        bytes_read += 2
    if command_nibble == 0xC:
        # Patch Change
        print('Patch Change')
        instrument = get_bytes(midi_file, 1)
        bytes_read += 1
    if command_nibble == 0xD:
        # Channel Pressure
        print('Channel Pressure')
        channel_pressure = get_bytes(midi_file, 1)
        bytes_read += 1
    if command_nibble == 0xE:
        # Pitch Bend
        print('Pitch Bend')
        lsb = get_bytes(midi_file, 1)
        msb = get_bytes(midi_file, 1)
        # Pitch bend is denoted by a 14 bit value
        # 0mmmmmmm 0lllllll -> mmmmmmmlllllll
        bytes_read += 2
    if command_nibble == 0xF:
        # System Event
        print('System Event')
        system_bytes, system_event = parse_system_event(midi_file, channel_nibble)
        bytes_read += system_bytes
        pass
    return bytes_read, None


def get_track_event(midi_file):
    v_time_length, v_time = get_variable_time(midi_file)
    event_length, event = parse_event(midi_file)

    return v_time_length + event_length, event


def parse_track(midi_file, delta):
    track_header = get_bytes(midi_file, 4)
    if track_header != 0x4d54726b:
        raise ValueError('Invalid Track header')

    track_length = get_bytes(midi_file, 4)
    track_events = []
    bytes_processed = 0
    while bytes_processed < track_length:
        track_event_length, event = get_track_event(midi_file)
        bytes_processed += track_event_length
        track_events.append(event)
    return track_events


with open('world-1-birabuto.mid', 'rb') as f:
    midi_format, num_track_chunks, division = parse_header(midi_file=f)

    if midi_format == Format.MULTI_SONG:
        raise ValueError('Multi song midi not supported currently')
    if midi_format > 2:
        raise ValueError('Invalid midi format')

    tracks = [parse_track(midi_file=f, delta=division) for track in range(num_track_chunks)]
    print(tracks)
