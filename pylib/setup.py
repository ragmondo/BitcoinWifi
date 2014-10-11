from distutils.core import setup, Extension

module1 = Extension('bcnet',
                    sources = ['bcnetmodule.c'])

setup (name = 'BcNet',
       version = '1.0',
       description = 'Bitcoin wifi net package',
       ext_modules = [module1])
