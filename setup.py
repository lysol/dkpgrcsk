#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(name='dkpgrcsk',
      version='1.1',
      description='Simple, extensible irclib based IRC bot.',
      author='Derek Arnold',
      author_email='derek@derekarnold.net',
      url='http://lysol.github.com/dkpgrcsk',
      packages=['dkpgrcsk', 'dkpgrcsk/plugins'],
      package_dir={'dkpgrcsk': 'src/dkpgrcsk',
            'dkpgrcsk/plugins': 'src/dkpgrcsk/plugins'},
      include_package_data=True,
      license='BSD',
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Programming Language :: Python :: 2.7"
      ],
      download_url="http://github.com/lysol/dkpgrcsk/tarball/v1.1",
      requires=(
        'pymblr',
        'python_irclib'
        )
     )
