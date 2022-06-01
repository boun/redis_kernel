from setuptools import setup
from setuptools.command.install import install
import json
import os.path
import sys
from redis_kernel.constants import *

if sys.version_info.major != 3 or sys.version_info.minor < 6:
    sys.exit('We supports Python 3.6+ only')


kernel_json = {"argv":[sys.executable,"-m", NAME, "-f", "{connection_file}"],
 "display_name": DISPLAY_NAME,
 "language": LANGUAGE,
 "codemirror_mode": "shell"
}

class Installer(install):
	def run(self):
		# Regular installation
		install.run(self)

		# Now write the kernelspec
		from jupyter_client.kernelspec import KernelSpecManager
		from IPython.utils.tempdir import TemporaryDirectory
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
                        'jupyter_client',
                        'ipykernel',
                        'metakernel'],
	  classifiers = [
		  'Framework :: IPython',
		  'Programming Language :: Python :: 3.6',
		  'Programming Language :: Python :: 3',
          'Development Status :: 3 - Alpha',
		  'Topic :: System :: Shells',
	  ]
)
