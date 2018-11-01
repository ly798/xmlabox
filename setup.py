from setuptools import setup, find_packages

PACKAGE = "xmlabox"
VERSION = __import__(PACKAGE).__version__

setup(name=PACKAGE,
      version=VERSION,
      packages=find_packages(),
      author='yang',
      author_email='yippeetry@gmail.com',
      description='',
      url="https://github.com/ly798/xmlabox",
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools', 'python-vlc', 'requests', 'wcwidth'],
      entry_points={
          'console_scripts': ['xmlabox = xmlabox.main:main'],
      },
      classifiers=[
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
      ])
