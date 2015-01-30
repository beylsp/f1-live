"""
A collection of dump utilities.

  - hexdump() utility is a filter which displays the data input in hexadecimal
    format.

    > hexdump("Lorem ipsum dolor sit amet, consectetur adipisicing elit, ...")
    0x0000: 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f  Lorem ipsum dolo
    0x0010: 7220 7369 7420 616d 6574 2c20 636f 6e73  r sit amet, cons
    0x0020: 6563 7465 7475 7220 6164 6970 6973 6963  ectetur adipisic
    0x0030: 696e 6720 656c 6974 2c20 2e2e 2e         ing elit, ...

  - binary() utility is a filter which displays the data input in binary
    format.

    > binary("\\xfe")
    01111111
"""
import binascii

__all__ = ['hexdump', 'binary']

def dump(data, size=4):
    """dump binary data in chunks of 2 octets."""
    hexstr = binascii.hexlify(data)
    return ' '.join(genchunks(hexstr, size))

def genchunks(seq, size):
    """yield chunks of size from seq"""
    quotient, rest = divmod(len(seq), size)
    for i in range(quotient):
        yield seq[i*size:(i+1)*size]
    if rest:
        yield seq[quotient*size:]

def genhex(data):
    """yield lines in hex format including address info and printable chars."""
    line = ''
    generator = genchunks(data, 16)
    for addr, dat in enumerate(generator):
        line = '0x%04X: ' % (addr*16)
        line += dump(dat)
        # add padding
        pad = 2
        if len(dat) < 16:
            rest = 16-len(dat)
            pad += 2*rest + rest/2
        line += ' '*pad

        for byte in dat:
            byte = ord(byte)
            if 0x20 <= byte <= 0x7E:
                line += chr(byte)
            else:
                line += '.'

        yield line

def hexdump(data, result='print'):
    """
    Dump data in hexadecimal format: either printing to standard output or
    yielding a generator.

    @param data: data to dump in hexadecimal format.
    @type data: C{string}.
    @param result: how to yield the result: 'print' (default) or 'generator'.
    @type result: C{string}.
    @return: generator yielding lines of data in hex format
             (if result requires this).
    @rtype: C{generator} or None.
    @raise ValueError: when value of 'result' argument is unknown.
    """
    gen = genhex(data)
    if result == 'print':
        for line in gen:
            print line
    elif result == 'generator':
        return gen
    else:
        raise ValueError("Unknown value of 'result' argument")

def genbit(data, endian):
    """yield octets in binary format."""
    generate = genchunks(data, 1)
    for byte in generate:
        bits = [0]*8
        for i in range(8):
            if ord(byte) & (0x80>>i):
                bits[i] = 1
        if endian == 'big':
            yield ''.join(str(bit) for bit in bits)
        elif endian == 'little':
            yield ''.join(str(bit) for bit in reversed(bits))
        else:
            raise ValueError("Unknown value of 'endian' argument")

def binary(data, endian='little', result='print'):
    """
    Dump data in binary format: either printing to standard output or
    yielding a generator.

    @param data: data to dump in binary format.
    @type data: C{string}.
    @param endian: endianness: 'little' (default) or 'big'.
    @type endian: C{string}
    @param result: how to yield the result: 'print' (default) or 'generator'.
    @type result: C{string}.
    @return: generator yielding octets of data in binary format
             (if result requires this).
    @rtype: C{generator} or None.
    @raise ValueError: when value of 'result' argument is unknown.
   """
    gen = genbit(data, endian)

    if result == 'print':
        print ' '.join(gen)
    elif result == 'generator':
        return gen
    else:
        raise ValueError("Unknown value of 'result' argument")

