import os


def find_files(path: str = ':', format: str = ''):
    return ['{path}/{file}'.format(path=p, file=f) for (p, ds, fs) in os.walk(path) for f in fs if f.endswith(format)]

