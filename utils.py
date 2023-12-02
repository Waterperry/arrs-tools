import os


def get_filenames(directory: str):
    names = []
    for _, _, filenames in os.walk(directory):
        for filename in filenames:
            names.append(filename)

    return names


def read_files_into_dict(directory: str):
    filenames = get_filenames(directory)
    contents_dict = {}
    for filename in filenames:
        file = open(os.path.join(directory, filename), 'r')
        contents_dict[filename] = file.readlines()

    return contents_dict


def c2s(code):
    file_str = code[1:]
    filename = 'DataStreamRay_' + file_str + '.txt'
    return filename


def get_line(line_code, from_dict: dict, index_starts_at_one=True):
    """
    Deprecated function which falsely assumes the code[x[AB_CD] refers to line x of file AB_CD (it does not)
    """
    filename = c2s(line_code)
    if index_starts_at_one:
        idx = int(line_code[0])
    else:
        idx = int(line_code[0]) - 1

    return from_dict[filename][idx]


def get_idx_of_group(group_key, line_code, from_dict):
    filename = c2s(line_code)
    lines_containing_group_key = []

    for line in from_dict[filename]:
        if group_key in line:
            lines_containing_group_key.append(line)

    idx = int(line_code[0]) - 1
    return lines_containing_group_key[idx]


def load_groups_and_keys() -> (list, list):
    group_strings = 'MTIxID,ExMSAx,MTcgMz'.split(",")
    key_strings = [string.split(" ") for string in "3[NZ_XX] 1[IY_TB] 2[MR_AG] 2[C3_DM],"
                                                   "2[MR_AG] 1[NZ_XX] 2[IY_TB] 2[C3_DM],"
                                                   "1[C3_DM] 1[MR_AG] 1[IY_TB] 1[NZ_XX]".split(",")]
    return group_strings, key_strings
