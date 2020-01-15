from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='dir2pdf',
    version='0.0.3',
    author='Jacob Komissar',
    description='Convert directories of images to PDFs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jirassimok/dir2pdf',

    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    py_modules=['dir2pdf'],

    python_requires='>=3.7',
    install_requires=['Pillow'],
    extras_require={
        'dev': ['flake8'],
    },
    entry_points={
        'console_scripts': ['dir2pdf = dir2pdf:main'],
    }
)
