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
        'signature': 'a0 89 5e fc 10 00 20 6d 5e f8 10 00 5e fc 10 00 42 b0 24 00 a2 40 e0 ff a2 41',
        'patch': '00 0c',
        'description': 'Patches the I2C write routine to force all LEDs to be on. This is the "original" winning patch from DEFCON 26.'
    }
}

PARAMETERIZED_PATCHES = {
    # 1d0097b8
    'badge_type': {
        'signature': '42 00 3c 2b 5e 18 00 00 5e 14 00 00 be 0f c3 4b 09 4c bf 45 b0 4f c1 cb dd 0f 44 0c',
        'parameterized_patch': 'XX ed 00 0C',
        'params': 1,
        'description': 'Patches the routine determining badge type to make your badge think it is of a different type. Valid values are 0-7.'
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
    return [int(x, 16) for x in h.split(' ')]


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


def perform_patch(ih, addr, byte_seq):
    for i, b in enumerate(byte_seq):
        ih[addr + i] = b


def parameterize_patch(patch, param):
    parsed_param = int(param)
    if parsed_param < 0 or parsed_param > 255:
        raise Exception('Invalid parameter - valid ranges are 0 to 255 inclusive')
    return patch.replace('XX', '%0.2X' % parsed_param)


def patch_file(args):
    ih = IntelHex()
    ih.loadhex(args.input_file)

    for patch_name in PATCHES:
        val = getattr(args, patch_name)
        if val is False:
            continue
        patch_data = PATCHES[patch_name]
        patch_bytes = convert_hex_str_to_list(patch_data['patch'])

        start_addr = search_for_patch_area(ih, convert_hex_str_to_list(patch_data['signature']))
        print('Applying patch {} at address {} ({} bytes)'.format(patch_name, '0x%0.8X' % start_addr, len(patch_bytes)))
        perform_patch(ih, start_addr, patch_bytes)

    for patch_name in PARAMETERIZED_PATCHES:
        val = getattr(args, patch_name)
        if val is None or len(val) == 0:
            continue

        patch_data = PARAMETERIZED_PATCHES[patch_name]
        patch_bytes = convert_hex_str_to_list(parameterize_patch(patch_data['parameterized_patch'], val[0]))

        start_addr = search_for_patch_area(ih, convert_hex_str_to_list(patch_data['signature']))
        print('Applying patch {} at address {} ({} bytes)'.format(patch_name, '0x%0.8X' % start_addr, len(patch_bytes)))
        perform_patch(ih, start_addr, patch_bytes)

    backup_file(args.input_file)
    sio = StringIO()
    ih.write_hex_file(sio)
    output = sio.getvalue()
    output = output.encode('utf-8').replace(b'\r\n', b'\n')
    with open(args.input_file, 'wb') as f:
        f.write(output)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patches the DEFCON26 badge firmware.')
    parser.add_argument('input_file', metavar='file', type=str, help='Path to a firmware hex to patch')

    for patch_name in PATCHES:
        patch_data = PATCHES[patch_name]
        parser.add_argument('--%s' % patch_name, help=patch_data['description'], action='store_true')
        
    for patch_name in PARAMETERIZED_PATCHES:
        patch_data = PARAMETERIZED_PATCHES[patch_name]
        parser.add_argument('--%s' % patch_name, help=patch_data['description'], nargs=patch_data['params'])

    args = parser.parse_args()
    
    patch_file(args)