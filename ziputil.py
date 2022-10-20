import zipfile
import os

def compress_files(base, f_list, dest):
    dest_file = os.path.join(dest, dest + '.zip')
    with zipfile.ZipFile(dest_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as f:
        progress_count = 0
        for file in f_list:
            f.write(os.path.join(base, file), arcname=file)
            # progress bar
            width = 20
            progress_count += 1
            c = int((progress_count/len(f_list))*width) + 1
            bar = '|'+(c*"-").ljust(width)  + '|'
            print(f'{bar}{progress_count}/{len(f_list)} compressing "{os.path.split(file)[-1]}"', end='')
            print(f'{" "*100}', end='\r') # clean line
            
    print(f'compress finish destination: {dest_file}')
    
def decompress_files(src, dest_dir):
    if not zipfile.is_zipfile(src):
        return False
    with zipfile.ZipFile(src, 'r') as f:
        file_list = f.namelist()
        progress_count = 0
        for file in file_list:
            f.extract(file, dest_dir)
            # progress bar
            width = 20
            progress_count += 1
            c = int((progress_count/len(file_list))*width) + 1
            bar = '|'+(c*"-").ljust(width)  + '|'
            print(f'{bar}{progress_count}/{len(file_list)} decompressing "{os.path.split(file)[-1]}"', end='')
            print(f'{" "*100}', end='\r') # clean line
    print(f'decompress finish destination: {dest_dir}')
    return True