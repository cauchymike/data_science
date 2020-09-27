import os
import mimetypes
import arrow


additional_file_types = {
    '.md': 'text/markdown'
}


def datetimeformat(date_str):
    dt = arrow.get(date_str)
    return dt.humanize()


def file_type(key):
    file_info = os.path.splitext(key)
    file_extension = file_info[1]
    try:
        return mimetypes.types_map[file_extension]
    except KeyError:
        filetype = 'Unknown'
        if file_info[0].startswith('.') and file_extension == '':
            filetype = 'text'

        if file_extension in additional_file_types.keys():
            filetype = additional_file_types[file_extension]

        return filetype
    
def convert_bytes(num):
    "converting byte to mb"
    if num == 0:
        return "0B"
    size_name = ('B', 'KB', 'MB', 'GB', 'TB')
    i = int(math.floor(math.log(num, 1024)))
    p = math.pow(1024, i)
    s = round(num/p, 2)
    return f"{s}{size_name[i]}"
