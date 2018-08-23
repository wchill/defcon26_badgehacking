import os
import sys
import datetime
from intelhex import IntelHex
import shutil
from io import StringIO
import argparse


PATCHES = {
    # 1d020152
    'all_leds_on': {
        'patches': [
            {
                'signature': 'a0 89 5e fc 10 00 20 6d 5e f8 10 00 5e fc 10 00 42 b0 24 00 a2 40 e0 ff a2 41',
                'patch': '00 0c',
            }
        ],
        'description': 'Patches the I2C write routine to force all LEDs to be on. This is the "original" winning '\
                       'patch from DEFCON 26.'
    },
    'dump_memory': {
        'patches': [
            {
                'address': 0x1d030000,
                'patch': '00 fa bd 27 fc ff bf af f8 ff be af 21 f0 1d 00 00 fa c0 af 80 ff c8 23 34 58 01 3c 25 30 29 34 00 00 09 ad 04 00 00 ad 00 ff c4 23 80 ff c5 23 21 30 00 00 02 9d 01 3c 7c 2d 28 34 09 f8 00 01 00 00 00 00 00 fa c4 27 00 ff c5 27 00 9d 01 3c 8c 01 28 34 09 f8 00 01 00 00 00 00 00 fa c4 27 02 9d 01 3c f4 20 28 34 09 f8 00 01 00 00 00 00 00 80 01 3c 64 03 24 34 00 fa c5 27 21 30 02 00 d0 09 01 3c 18 95 28 34 09 f8 00 01 00 00 00 00 21 e8 1e 00 f8 ff be 8f fc ff bf 8f 00 06 bd 27 08 00 e0 03 00 00 00 00'
            },
            {
                'signature': '5e 30 1c 00 a3 41 02 9d c3 fc 5c f7',
                'patch': 'a8 41 03 9d 88 45 00 0c'
            }
        ],
        'description': 'Add a memory dump routine to the service menu, replacing the "get BB buffer" option. '\
                       'Currently doesn\'t work.'
    },
    # 1d01a0f4
    'fix_p1': {
        'patches': [
            {
                'signature': '42 70 05 00 42 b0 01 00 2d 2d 82 0c 5e fc',
                'patch': '42 70 01 00'
            },
        ],
        'description': 'Fixes the bug in hardware puzzle 1 that prevents E from turning green, even when C11 is '\
                       'shorted.'
    },
    'solve_p1': {
        'patches': [
            {
                'signature': '1e 18 00 00 a2 41 80 bf 42 fc d0 2d 42 00 ec 00 2d 2d 62 0c 5e 14 00 00',
                'patch': 'a3 41 80 bf 04 ed 43 18 e8 2b 43 fc d0 2d 42 00 ec 00 2d 2d 00 0c 00 0c 00 0c'
            },
            {
                'signature': 'd3 44 42 00 3c 2b 5e 18 00 00 5e 14 00 00 be 0f c3 4b 09 4c bf 45 00 0c',
                'patch': '00 0c'
            }
        ],
        'description': 'Pulls RA2 high, forcing the LED next to C11 to always be on without actually having to '\
                       'short C11. On a human badge, this reconfigures the ARC Networks console and solves hardware '\
                       'puzzle 1. Note that on v0 and v1 firmwares, the fix_p1 patch is also required.'
    },
}

PARAMETERIZED_PATCHES = {
    # 1d0097b8
    'badge_type': {
        'signature': '42 00 3c 2b 5e 18 00 00 5e 14 00 00 be 0f c3 4b 09 4c bf 45 b0 4f c1 cb dd 0f 44 0c',
        'parameterized_patch': 'XX ed 00 0C',
        'params': 1,
        'description': 'Patches the routine determining badge type to make your badge think it is of a different '\
                       'type. Valid values are 0-7.'
    }
}

FLASH_PATCHES = {
    'pairing_byte': {
        'address': 0x1d03f800,
        'params': 1,
        'description': 'Overwrite the bitfield containing the state of badge pairings. 0 means all badges have been '\
                       'paired with, 255 means there have been no pairings.'
    },
    'karma_byte': {
        'address': 0x1d03f801,
        'params': 1,
        'description': 'Overwrite the bitfield containing the karma of paired badges. 0 means that all badge types '\
                       'have good karma (green N), 255 means all badge types have neutral or bad karma (red N). Note '\
                       'that this is distinct from the pairing state and you need both pairing and karma at 0 '\
                       'to officially solve the puzzle.'
    }
}


def eprint(s):
    print(s, file=sys.stderr)


def backup_file(path):
    dirname = os.path.dirname(path)
    name, ext = os.path.splitext(os.path.basename(path))
    backup_name = '{}-backup-{}{}'.format(
        name,
        datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
        ext)
    shutil.copyfile(path, os.path.join(backup_name))


def convert_hex_str_to_list(h):
    return [validate_byte(int(x, 16)) for x in h.split(' ')]


def search_for_patch_area(ih, byte_seq):
    addr = 0x1d000000
    end_addr = addr + 0x40000

    result = []

    for i in range(addr, end_addr, 2):
        if ih[i] == byte_seq[0]:
            valid = True
            for j, b in enumerate(byte_seq):
                if ih[i+j] != b:
                    valid = False
                    break
            if valid:
                result.append(i)

    if len(result) == 0:
        raise Exception('Couldn\'t find a patch target for byte seq {}'.format(' '.join(['%0.2X' % x for x in byte_seq])))
    elif len(result) > 1:
        raise Exception('Found {} patch targets: {}'.format(len(result), ' '.join(['0x%0.8X' % x for x in result])))
    else:
        return result[0]


def perform_patch(ih, patch_name, addr, byte_seq):
    print('Applying patch {} at address {} ({} byte(s))'.format(patch_name, '0x%0.8X' % addr, len(byte_seq)))
    for i, b in enumerate(byte_seq):
        ih[addr + i] = validate_byte(b)


def validate_byte(b):
    if b < 0 or b > 255:
        raise Exception('Received a value that was not a valid byte: {}'.format(b))
    return b


def parameterize_patch(patch, param):
    return patch.replace('XX', '%0.2X' % validate_byte(param))


def do_patches(ih, args):
    for patch_name in PATCHES:
        val = getattr(args, patch_name)
        if val is False:
            continue

        patch_data = PATCHES[patch_name]
        patch_list = patch_data['patches']

        for patch in patch_list:
            patch_bytes = convert_hex_str_to_list(patch['patch'])
            start_addr = None

            if 'signature' in patch:
                start_addr = search_for_patch_area(ih, convert_hex_str_to_list(patch['signature']))
            else:
                start_addr = patch['address']

            perform_patch(ih, patch_name, start_addr, patch_bytes)


def do_parameterized_patches(ih, args):
    for patch_name in PARAMETERIZED_PATCHES:
        val = getattr(args, patch_name)
        if val is None:
            continue

        patch_data = PARAMETERIZED_PATCHES[patch_name]
        patch_bytes = convert_hex_str_to_list(parameterize_patch(patch_data['parameterized_patch'], val[0]))
        start_addr = search_for_patch_area(ih, convert_hex_str_to_list(patch_data['signature']))
        perform_patch(ih, patch_name, start_addr, patch_bytes)


def do_flash_patches(ih, args):
    for patch_name in FLASH_PATCHES:
        val = getattr(args, patch_name)
        if val is None:
            continue

        patch_data = FLASH_PATCHES[patch_name]
        start_addr = patch_data['address']
        perform_patch(ih, patch_name, start_addr, val)

        
def do_arbitrary_patches(ih, args):
    patches = args.patch
    if patches is None:
        return

    for patch in patches:
        if len(patch) < 2:
            continue
        addr = patch[0]
        patch_bytes = patch[1:]
        perform_patch(ih, 'arbitrary_patch', addr, patch_bytes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patches the DEFCON26 badge firmware.')
    parser.add_argument('input_file', metavar='file', type=str, help='Path to a firmware hex to patch')

    for patch_name in PATCHES:
        patch_data = PATCHES[patch_name]
        parser.add_argument('--%s' % patch_name, help=patch_data['description'], action='store_true')
        
    for patch_name in PARAMETERIZED_PATCHES:
        patch_data = PARAMETERIZED_PATCHES[patch_name]
        parser.add_argument('--%s' % patch_name, help=patch_data['description'], type=int, nargs=patch_data['params'])
        
    for patch_name in FLASH_PATCHES:
        patch_data = FLASH_PATCHES[patch_name]
        parser.add_argument('--%s' % patch_name, help=patch_data['description'], type=int, nargs=patch_data['params'])

    parser.add_argument('--patch', help='Performs an arbitrary memory patch. Specify address, then bytes. Can be specified multiple times.', action='append', nargs='+')

    args = parser.parse_args()

    ih = IntelHex()
    ih.loadhex(args.input_file)
    
    do_patches(ih, args)
    do_parameterized_patches(ih, args)
    do_flash_patches(ih, args)
    do_arbitrary_patches(ih, args)

    backup_file(args.input_file)
    sio = StringIO()
    ih.write_hex_file(sio)
    output = sio.getvalue()
    output = output.encode('utf-8').replace(b'\r\n', b'\n')
    with open(args.input_file, 'wb') as f:
        f.write(output)