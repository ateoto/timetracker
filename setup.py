from setuptools import setup, find_packages

setup(
    name='TimeTracker',
    version='0.1',
    url='https://github.com/Ateoto/timetracker/',
    author='Matthew McCants',
    author_email='mattmccants@gmail.com',
    description=('A simple time tracking and management tool.'),
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': [
        'tt = timetracker:process_commands',
    ]},
)