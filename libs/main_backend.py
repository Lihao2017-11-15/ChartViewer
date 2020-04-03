import os

def short(old_string):
    index = None
    new_string = ''
    for i in range(len(old_string)):
        index = len(old_string) - i - 1
        if old_string[index] == '\\':
            break

    for i in range(index + 1, len(old_string)):
        new_string += old_string[i]

    return new_string

def get_save_path(chart_type, directory_path):
    chart_idx = 0

    while True:
        chart_idx += 1
        filename = '{}_{}.{}'.format(chart_type, chart_idx, 'png')
        save_path = os.path.join(directory_path, filename)
        if not os.path.isfile(save_path):
            break

    return save_path

