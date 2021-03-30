from setuptools import setup
from sphinx.setup_command import BuildDoc


cmdclass = {'build_sphinx': BuildDoc}
name = 'weather',
version='0.0.1',
release='0.0.1'

setup(
    name=name,
    author=['Bartenev', 'Kulagin'],
    author_email='b.bar1enev@gmail.com',
    url='https://github.com/Flamer322/bot',
    version=release,
    cmdclass=cmdclass,
    packages=['weather'],
    install_requires=[
        'requests',
        'pytelegrambotapi',
        'sphinx',
        'importlib; python_version == "3.9"',
    ],
    #command_options={
    #    'build_sphinx': {
    #        'project': ('setup.py', name),
    #        'version': ('setup.py', version),
    #        'release': ('setup.py', release),
    #        'source_dir': ('setup.py', 'doc')}},
)