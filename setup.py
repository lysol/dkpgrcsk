#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(name='Douglbutt',
      version='1.0',
      description='Simple, extensible irclib based IRC bot.',
      author='Derek Arnold',
      author_email='derek@brainindustries.com',
      url='http://lysol.github.com/douglbutt',
      packages=['douglbutt', 'douglbutt/plugins'],
      package_dir={'douglbutt': 'src/douglbutt',
            'douglbutt/plugins': 'src/douglbutt/plugins'},
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
      download_url="http://github.com/lysol/douglbutt/tarball/v1.0" 
     )
