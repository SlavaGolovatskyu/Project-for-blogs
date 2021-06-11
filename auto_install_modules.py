import platform, os

requirements = open('requirements.txt', 'r').readlines()

msg = ''

if platform.system() == "Linux":
    msg = 'pip3'
else:
    msg = 'pip'


for module in requirements:
    print('-' * len(f'Installing module {module}' + '----\n'))
    print(f'   Installing module {module}   ')
    os.system(f'{msg} install {module}')
    print(f'Module {module} has installed')


print('Script end work.')