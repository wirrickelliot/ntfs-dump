from datetime import datetime, timedelta
import argparse

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('image')
parser.add_argument('offset', type=int)
args = parser.parse_args()

# get $MFT offset
f = open(args.image, 'rb')
f.seek(args.offset + 11)
bytes_per_sector = int.from_bytes(f.read(2), 'little')
sectors_per_cluster = int.from_bytes(f.read(1), 'little')
cluster_size = bytes_per_sector * sectors_per_cluster
f.seek(34, 1)
mft_cluster = int.from_bytes(f.read(8), 'little')
mft_offset = args.offset + cluster_size * mft_cluster

# loop through file records
directory = {}
entry = 26
while True:
    entry += 1
    file_entry_offset = mft_offset + (1024 * entry)

    # get attribute offset
    f.seek(file_entry_offset)
    if f.read(5) != b'FILE0':
        break
    f.seek(15, 1)
    attribute_offset = int.from_bytes(f.read(2), 'little')
    f.seek(file_entry_offset + attribute_offset)
    if f.read(4) == b'\xff\xff\xff\xff':
        continue
    else:
        f.seek(-4, 1)

    # skip $STANDARD_INFORMATION attribute
    attribute_type = f.read(4)
    standard_info_length = int.from_bytes(f.read(4), 'little')
    f.seek(file_entry_offset + attribute_offset + standard_info_length)

    # parse $FILE_NAME attribute
    file_name_start = f.tell()
    attribute_type = int.from_bytes(f.read(4), 'little')
    file_name_length = int.from_bytes(f.read(4), 'little')
    f.seek(16, 1)
    parent_directory = int.from_bytes(f.read(6), 'little')
    f.seek(2, 1)
    c_time = int.from_bytes(f.read(8), 'little') / 10
    a_time = int.from_bytes(f.read(8), 'little') / 10
    f.seek(16, 1)
    allocated_size = int.from_bytes(f.read(8), 'little')
    real_size = int.from_bytes(f.read(8), 'little')
    flags = f.read(4)
    f.seek(4, 1)
    filename_length = int.from_bytes(f.read(1), 'little')
    f.seek(1, 1)
    filename = f.read(filename_length * 2).decode('utf-8', 'replace').replace('\x00', '')
    f.seek(file_name_start + file_name_length)

    # skip $SECURITY_DESCRIPTOR attribute
    f.seek(4, 1)
    security_desc_length = int.from_bytes(f.read(4), 'little')
    f.seek(security_desc_length - 8, 1)
    
    # parse $DATA attribute
    file_signature = ''
    data_start = f.tell()
    if f.read(4) == b'\x80\x00\x00\x00':
        f.seek(4, 1)
        non_resident = int.from_bytes(f.read(1), 'little')
        name_length = int.from_bytes(f.read(1), 'little')

        # get data run
        if non_resident == 0:
            f.seek(data_start + (2 * name_length) + 24)
            file_signature = f.read(8)
        else:
            f.seek(38, 1)
            real_size = int.from_bytes(f.read(8), 'little')
            f.seek(data_start + (2 * name_length) + 64)
            data_run_header = int.from_bytes(f.read(1), 'little')
            num_offset_bytes = (data_run_header // 16) % 16
            num_size_bytes = data_run_header % 16
             
            data_length = int.from_bytes(f.read(num_size_bytes), 'little')
            data_offset = int.from_bytes(f.read(num_offset_bytes), 'little') * 4096

            f.seek(args.offset + data_offset)
            file_signature = f.read(8)

    # set file type
    if flags == b' \x00\x00\x10':
        file_type = 'Directory'
    elif file_signature.startswith(b'\x89PNG'):
        file_type = 'PNG image data'
    elif file_signature.startswith(b'GIF87a'):
        file_type = 'GIF image data'
    elif file_signature.startswith(b'GIF89a'):
        file_type = 'GIF image data'
    elif file_signature.startswith(b'%PDF'):
        file_type = 'PDF document'
    elif file_signature.startswith(b'MZ'):
        file_type = 'DOS MZ executable file'
    elif file_signature.startswith(b'<html>'):
        file_type = 'HTML document'
    elif file_signature.startswith(b'\xff\xfb'):
        file_type = 'MPEG ADTS layer III'
    elif file_signature.startswith(b'\xff\xf3'):
        file_type = 'MPEG ADTS layer III'
    elif file_signature.startswith(b'\xff\xf2'):
        file_type = 'MPEG ADTS layer III'
    elif file_signature.startswith(b'\x00\x00\x01\xba'):
        file_type = 'MPEG sequence'
    elif file_signature.startswith(b'\x00\x00\x01\xb3'):
        file_type = 'MPEG sequence'
    elif file_signature.startswith(b'\x00\x00\x01\xb3'):
        file_type = 'MPEG sequence'
    elif file_signature.startswith(b'\xff\xd8\xff\xdb'):
        file_type = 'JPEG image data'
    elif file_signature.startswith(b'\xff\xd8\xff\xe0'):
        file_type = 'JPEG image data'
    elif file_signature.startswith(b'\xff\xd8\xff\xee'):
        file_type = 'JPEG image data'
    elif file_signature.startswith(b'\xff\xd8\xff\xe1'):
        file_type = 'JPEG image data'
    else:
        file_type = 'ASCII text'

    # get file path
    directory[entry] = (filename, parent_directory)
    file_path = '' if parent_directory in directory.keys() else '/'
    while parent_directory in directory.keys():
        file_path = '/%s%s' % (directory[parent_directory][0], file_path)
        parent_directory = directory[parent_directory][1]

    # print values
    print("%s:" % entry)
    print("\tFile Name: %s" % filename)
    print("\tFile Path: %s" % file_path)
    print("\tFile Type: %s" % file_type)
    print("\tDate Created: %s UTC" % str(datetime(1601, 1, 1) + timedelta(microseconds=c_time)))
    print("\tDate Modified: %s UTC" % str(datetime(1601, 1, 1) + timedelta(microseconds=a_time)))
    print("\tAllocated Size: %d bytes" % allocated_size)
    print("\tReal Size: %d bytes" % real_size)

f.close()
