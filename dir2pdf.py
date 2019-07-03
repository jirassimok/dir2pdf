#!/usr/bin/env python3
"""
Convert the images in a directory to a PDF.
"""
import os, sys

from pathlib import Path

from PIL import Image

def exit(*message, code=1):
    """Print an optional error message and exit with the given status
    """
    if message:
        print('error:', *message, file=sys.stderr)
    sys.exit(code)

def dir2pdf(dir_path, pdf_path, title, author):
    """Convert the files in the given directory into a PDF
    """
    files = sorted(dir_path.iterdir())

    # Save the title page with metadata
    with Image.open(files[0]) as im:
        im.save(pdf_path,
                format='PDF',
                title=title,
                author=author,
                producer='dir2pdf')

    for file in files[1:]:
        with Image.open(file) as im:
            im.save(pdf_path, format='PDF', append=True)


if __name__ == '__main__':
    # args are directory, pdf, title, and author
    if len(sys.argv) != 5:
        print('usage: dir2pdf DIR PDF TITLE AUTHOR', file=sys.stderr)
        exit(1)

    dir_path, pdf_path = Path(sys.argv[1]), Path(sys.argv[2])
    title, author = sys.argv[3:]

    if not dir_path.is_dir():
        exit(f'{dir_path} is not a directory')
    try:
        next(dir_path.iterdir())
    except StopIteration:
        exit(f'no files in {dir_path}')

    if pdf_path.exists():
        exit(f'{pdf_path} already exists')

    dir2pdf(dir_path, pdf_path, title, author)
