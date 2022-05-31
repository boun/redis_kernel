from __future__ import absolute_import
from .kernel import *

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=RedisKernel)
