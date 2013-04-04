from setuptools import setup, find_packages
import os

ldesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='archversion',
    version=0,
    description='Archlinux Version Controller',
    long_description=ldesc,
    author='Sébastien Luttringer',
    license='GPL2',
    install_requires = ['xdg'],
    scripts=['bin/archversion'],
	packages=find_packages(),
    data_files=(
	  ('/usr/share/archversion/', ('README.rst', 'LICENSE', 'COPYRIGHT')),
      ('/usr/share/doc/archversion/', ('misc/archversion.conf', ))
    ),
    classifiers=[
        'Operating System :: Unix',
        'Programming Language :: Python',
        ],
    )
