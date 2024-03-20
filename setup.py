import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='pl-notification',
    version='0.0.1',
    author='FNNDSC',
    author_email='dev@babyMRI.org',
    description='A ChRIS Plugin for notification through mail / Slack / Element',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    py_modules=['notification'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'notification = notification:main',
        ]
    },
    install_requires=[
        'chris_plugin',
        'pflog',
        'pyyaml',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
)
