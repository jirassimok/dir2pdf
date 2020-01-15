#!/usr/bin/env python3
"""
Convert the images in a directory to a PDF.

Exit codes:
- 1 :: Application error
- 2 :: Argument error
"""
import re
import sys
import warnings

from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from PIL import Image


def configure_warnings(progname):
    def showwarning(message, category, filename, lineno, file=None, line=None):
        """Write a warning to a file. Replaces warnings.showwarning.
        """
        # Implementation based on warnings.showwarning
        if file is None:
            file = sys.stderr
            if file is None:
                return  # no stderr in pythonw.exe; warning lost
        try:
            file.write(f'{progname}: {category.__name__}: {message}\n')
        except OSError:
            pass  # error writing message; warning lost

    warnings.showwarning = showwarning


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
    if image.mode in {'RGBA', 'LA', 'PA'}:
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
            continue
        elif not subdir.is_dir():
            warnings.warn(f'Matching file {subdir} is not a directory;'
                          ' ignored')
            continue

        if 'n' in match.groupdict():
            n = match.group('n')
        elif match.groups():
            n = match.group(1)
        else:
            n = match.group(0)

        if not n:
            warnings.warn(f'Empty capturing group for {subdir};'
                          ' using name instead')
            n = subdir.name

        pdf = Path(str(pdf_path).format(n))

        if not append and pdf.exists():
            warnings.warn(f'skipping file {pdf}: file already exists')
            continue

        dir2pdf(subdir, pdf, title, author, append)


def argparser():
    parser = ArgumentParser(
        description='Convert images from a directory into a PDF',
        epilog='''
        If --subdirs is given, a PDF is generated for each subdirectory. The
        given PDF name is used as a format string, with {} replaced by a group
        from the matched string for each subdirectory.

        The named group 'n' is used if present, or the first capturing group
        otherwise. If the match has no capturing groups, the entire match
        string is used. If that value is empty, the name of the subdirectory is
        used instead.

        The replacement allows a format specification as in Python's str.format
        function.''')

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
    """Argparser argument type for regular expressions"""
    try:
        return re.compile(arg)
    except re.error as e:
        raise ArgumentTypeError(e.msg)


def main():
    # args are directory, pdf, title, and author
    parser = argparser()
    args = parser.parse_args()

    def exit(msg):
        sys.exit(f'{parser.prog}: error: {msg}')

    configure_warnings(parser.prog)

    if args.subdirs is not None:
        if '{}' not in str(args.pdf):
            parser.error(
                'if --subdirs is given, PDF must contain format field {}')
    elif not args.append and args.pdf.exists():
        exit(f'{args.pdf} already exists')

    if not args.dir.is_dir():
        exit(f'{args.dir} is not a directory')
    try:
        next(args.dir.iterdir())
    except StopIteration:
        exit(f'no files in {args.dir}')

    if args.subdirs is None:
        dir2pdf(args.dir, args.pdf, args.title, args.author, args.append)
    else:
        subdirs2pdf(args.dir, args.pdf, args.subdirs,
                    args.title, args.author, args.append)


if __name__ == '__main__':
    main()
