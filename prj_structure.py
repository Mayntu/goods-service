import os

def print_structure(start_path='.', prefix=''):
    items = sorted(os.listdir(start_path))
    for index, item in enumerate(items):
        path = os.path.join(start_path, item)
        connector = '└── ' if index == len(items) - 1 else '├── '
        print(prefix + connector + item)
        if os.path.isdir(path) and "venv" not in path and "env" not in path and "cache" not in path and "git" not in path:
            extension = '    ' if index == len(items) - 1 else '│   '
            print_structure(path, prefix + extension)

if __name__ == '__main__':
    print('Project structure:\n')
    print_structure('.')
