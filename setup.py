#!/usr/bin/env python
import json
import os
import sys
from setuptools import setup
from setuptools.command.install import install

NAME = 'redis_kernel'
VERSION = '0.6.0'
LANGUAGE = 'redis'
DISPLAY_NAME = 'Redis'
DESCRIPTION = 'A redis kernel for IPython'

if sys.version_info.major != 3 or sys.version_info.minor < 6:
    sys.exit('We supports Python 3.6+ only')


class Installer(install):
    def run(self):
        # Regular install
        install.run(self)

        # Post install
        print('Installing Jupyter kernelspec')
        from jupyter_client.kernelspec import KernelSpecManager
        from IPython.utils.tempdir import TemporaryDirectory
        kernel_json = {
            "argv":[sys.executable,"-m", NAME, "-f", "{connection_file}"],
            "codemirror_mode": "shell",
         "display_name": DISPLAY_NAME,
         "language": LANGUAGE
        }
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            ksm = KernelSpecManager()
            ksm.install_kernel_spec(td, 'redis', user=self.user, replace=True, prefix=self.prefix)

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name = NAME,
      version = VERSION,
      description= DESCRIPTION,
      long_description='Please check https://github.com/boun/redis_kernel',
      author='boun',
      author_email='boun@gmx.de',
      url='https://github.com/boun/redis_kernel',
      packages=[ NAME ],
      cmdclass={'install': Installer},
      include_package_data=True,
      install_requires=['jupyter>=1.0.0',
                        'ipykernel',
                        'metakernel',
                        'jupyter_client'],
      classifiers = [
          'Framework :: IPython',
          'Programming Language :: Python :: 3',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Science/Research',
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Shells',
      ])
