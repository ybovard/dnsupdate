from setuptools import setup
import glob


setup(name = "dnsupdate",
    version = "0.1.1",
    description = "DNS Updater for A and AAAA records",
    author = "__AUTHORNAME__",
    url='__WEBSITE__',
    author_email = "__AUTHOREMAIL__",
    package_dir={'':'src'},
    packages = ['dnsupdate',],
    entry_points={
        'console_scripts': [
           'dnsupdate=dnsupdate:main ',
        ],
    },
    long_description = """DNS Updater for A and AAAA records""" ,
    data_files=[
               ('/etc/dnsupdate',glob.glob('conf/*.dist')),
               ('/etc/dnsupdate/conf.d',glob.glob('conf/conf.d/*.dist')),
                ]
) 
