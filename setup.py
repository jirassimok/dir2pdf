from setuptools import setup

setup(
    name='dir2pdf',
    version='1.0.0',
    author='Jacob Komissar',
    description='Convert directories of images to PDFs',
    python_requires='>=3.7',
    py_modules=['dir2pdf'],
    install_requires=['Pillow'],
    extras_require={
        'dev': ['flake8'],
    },
    entry_points={
        'console_scripts': ['dir2pdf = dir2pdf:main'],
    }
)
