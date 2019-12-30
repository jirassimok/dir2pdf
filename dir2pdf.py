#!/usr/bin/env python3
"""
Convert the images in a directory to a PDF.
"""
import re
import sys
import warnings

from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from PIL import Image


def dir2pdf(dir_path, pdf_path, title=None, author=None, append=False):
    """Convert the files in the given directory into a PDF
    """
    files = sorted(dir_path.iterdir())

    # Save the title page with metadata
    with Image.open(files[0]) as im:
        im = remove_transparency(im, files[0])
        im.save(pdf_path,
                format='PDF',
                title=title,
                author=author,
                producer='dir2pdf',
                append=append)

    for file in files[1:]:
        with Image.open(file) as im:
            im = remove_transparency(im, file)
            im.save(pdf_path, format='PDF', append=True)


def remove_transparency(image, filename):
    if image.mode == 'RGBA':
        if image.getchannel('A').getextrema() != (255, 255):
            warnings.warn(f"Image '{filename}' contains transparency;"
                          " color will be off")
        return image.convert('RGB')
    else:
        return image


def subdirs2pdf(basedir_path, pdf_path, subdir_regex,
                title=None, author=None, append=False):
    for subdir in sorted(basedir_path.iterdir()):
        match = subdir_regex.match(subdir.name)

        if not match:
            warnings.warn(f'skipping subdir {subdir}:'
                          ' did not match subdir regex')
            continue

        if 'n' in match.groupdict():
            n = match.group('n')
        elif match.groups():
            n = match.group(1)
        else:
            n = match.group(0)

        pdf = Path(str(pdf_path).format(n))

        if not append and pdf.exists():
            warnings.warn(f'skipping file {pdf}: file already exists')
            continue

        dir2pdf(subdir, pdf, title, author, append)


def argparser():
    parser = ArgumentParser(
        description='Convert images from a directory into a PDF',
        epilog='''
        If --subdirs is given, A PDF is then generated for each subdirectory.
        The given PDF name is used as a format string, with {} substituted by
        the named group 'n', if present, or the first capturing group
        otherwise. If there are no capturing group, the entire match string is
        used in the name of the PDF. Errors may occur if the format field
        contains special filename characters.''')

    parser.add_argument('pdf', type=Path, help='The PDF to write')
    parser.add_argument('dir', type=Path, help='The directory to convert')
    parser.add_argument('--title', '-t', help='A title for the PDF')
    parser.add_argument('--author', help='The author of the document')

    parser.add_argument('--append', action='store_true',
                        help='Append to the PDF instead of writing')

    parser.add_argument('--subdirs', '-d', type=Regex, help=(
        "A regexp matching the base name of each subdirectory."))

    return parser


def Regex(arg):
    """Argument type for --subdirs regular expressions"""
    try:
        regex = re.compile(arg)
    except re.error as e:
        raise ArgumentTypeError(e.msg)
    if 'n' not in regex.groupindex and regex.groups < 1:
        raise ArgumentTypeError(
            "--subdirs regex must have at least one capturing group")
    return regex


if __name__ == '__main__':
    # args are directory, pdf, title, and author
    parser = argparser()
    args = parser.parse_args()

    if not args.dir.is_dir():
        sys.exit(f'{args.dir} is not a directory')
    try:
        next(args.dir.iterdir())
    except StopIteration:
        sys.exit(f'no files in {args.dir}')

    if args.subdirs is not None:
        if '{}' not in str(args.pdf):
            parser.error(
                'if --subdirs is given, PDF must contain format field {}')
    elif not args.append and args.pdf.exists():
        sys.exit(f'{args.pdf} already exists')

    if args.subdirs is None:
        dir2pdf(args.dir, args.pdf, args.title, args.author, args.append)
    else:
        subdirs2pdf(args.dir, args.pdf, args.subdirs,
                    args.title, args.author, args.append)
