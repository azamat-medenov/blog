import time
import random
import uuid
from uuid import UUID

sequenceCounter = 0
_last_v1timestamp = 0
_last_v6timestamp = 0
_last_v7timestamp = 0
_last_v8timestamp = 0
_last_uuid_int = 0
_last_sequence = None
uuidVariant = '10'


def uuid7(devDebugs: bool = False, returnType: str = 'hex') -> UUID:
    """Generates a 128-bit version 7 UUID with nanoseconds precision timestamp and random node
    example: 061cdd23-93a0-73df-a200-6ff3e72d92e9

    format: unixts|subsec_a|version|subsec_b|variant|subsec_seq_node
    """

    global _last_v7timestamp
    global _last_uuid_int
    global _last_sequence
    global sequenceCounter
    global uuidVariant
    uuidVersion = '0111'
    sec_bits = 36
    subsec_bits = 30
    version_bits = 4
    variant_bits = 2
    sequence_bits = 8
    node_bits = (128 - sec_bits - subsec_bits - version_bits - variant_bits - sequence_bits)

    timestamp = time.time_ns()

    subsec_decimal_digits = 9
    subsec_decimal_divisor = (10 ** subsec_decimal_digits)
    integer_part = int(timestamp / subsec_decimal_divisor)
    sec = integer_part

    fractional_part = round((timestamp % subsec_decimal_divisor) / subsec_decimal_divisor, subsec_decimal_digits)
    subsec = round(fractional_part * (2 ** subsec_bits))

    if devDebugs is True:
        print("Timestamp: " + str(timestamp))
        print("Sec: " + str(sec))
        print("Subsec Int: " + str(subsec))
        print("Subsec Dec: " + "{0:.9f}".format(fractional_part))
        test_timestamp = str(sec) + str("{0:.9f}".format(fractional_part)[-9:])
        if test_timestamp == str(timestamp):
            print("Good subsec math")
        else:
            print("Bad Subsec Math")

    unixts = f'{sec:036b}'
    subsec_binary = f'{subsec:030b}'
    subsec_a = subsec_binary[:12]
    subsec_b_c = subsec_binary[-18:]
    subsec_b = subsec_b_c[:12]
    subsec_c = subsec_binary[-6:]

    if timestamp <= _last_v7timestamp:
        sequenceCounter = int(sequenceCounter) + 1
        if devDebugs is True:
            print("Sequence: Incrementing Sequence to {0}".format(str(sequenceCounter)))
    if timestamp > _last_v7timestamp:
        sequenceCounter = 0
        if devDebugs is True:
            print("Sequence: Setting to {0}".format(str(sequenceCounter)))

    sequenceCounterBin = f'{sequenceCounter:08b}'

    _last_v7timestamp = timestamp
    _last_sequence = int(sequenceCounter)

    randomInt = random.getrandbits(node_bits)
    randomBinary = f'{randomInt:048b}'

    subsec_seq_node = subsec_c + sequenceCounterBin + randomBinary

    UUIDv7_bin = unixts + subsec_a + uuidVersion + subsec_b + uuidVariant + subsec_seq_node
    UUIDv7_int = int(UUIDv7_bin, 2)
    if devDebugs is True:
        if UUIDv7_int < _last_uuid_int and _last_uuid_int != 0:
            print("Error: UUID went Backwards!")
            print("UUIDv7 Last: " + str(_last_uuid_int))
            print("UUIDv7 Curr: " + str(UUIDv7_int))
    _last_uuid_int = UUIDv7_int

    UUIDv7_hex = f'{UUIDv7_int:032x}'
    UUIDv7_formatted = '-'.join(
        [UUIDv7_hex[:8], UUIDv7_hex[8:12], UUIDv7_hex[12:16], UUIDv7_hex[16:20], UUIDv7_hex[20:32]])

    if devDebugs is True:
        print("UUIDv7 Con: {0}|{1}|{2}|{3}|{4}|{5}".format(unixts,
                                                           subsec_a,
                                                           uuidVersion,
                                                           subsec_b,
                                                           uuidVariant,
                                                           subsec_seq_node))
        print("UUIDv7 Bin: {0} (len: {1})".format(UUIDv7_bin, len(UUIDv7_bin)))
        print("UUIDv7 Int: " + str(UUIDv7_int))
        print("UUIDv7 Hex: " + UUIDv7_formatted)
        print("\n")

    if returnType.lower() == "bin":
        return uuid.UUID(UUIDv7_bin)
    if returnType.lower() == "int":
        return uuid.UUID(str(UUIDv7_int))
    if returnType.lower() == "hex":
        return uuid.UUID(UUIDv7_formatted)

    raise ValueError('return type was not specified')
