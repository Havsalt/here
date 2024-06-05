__version__ = "0.2.4"

import pathlib
import argparse
import subprocess
import pyperclip as clipboard
import color
from color import paint


class ParserArgs(argparse.Namespace):
    silent: bool
    verbose: bool
    end: str
    where_mode: bool


parser = argparse.ArgumentParser(
    prog="here",
    usage="Copy 'here' path to clipboard"
    )
parser.add_argument("-v", "--version",
                    action="version",
                    version=f"%(prog)s: v{__version__}")
parser.add_argument("-w", "--from-where",
                    action="store_true",
                    dest="where_mode")
print_group = parser.add_mutually_exclusive_group()
print_group.add_argument("--verbose",
                         action="store_true")
print_group.add_argument("--silent",
                         action="store_true")
parser.add_argument("end",
                    nargs="?",
                    default=".",
                    help="Relative path to join with current working directory path")
args = ParserArgs()
parser.parse_args(namespace=args)

if args.where_mode:
    location = subprocess.check_output(["where", args.end], text=True)
    absolute_path = (
        pathlib.Path(location.rstrip("\n "))
        .resolve()
    )
else:
    absolute_path = (
        pathlib.Path
        .cwd()
        .joinpath(args.end)
        .resolve()
    )

if not args.silent:
    if args.verbose:
        print(paint("[Info]", color.AQUA),
              paint("Copying to clipboard", color.PINK) + paint(":", color.WHITE),
              paint(absolute_path, color.UNDERLINE + color.DARK_VIOLET))
    else:
        print(absolute_path)

clipboard.copy(str(absolute_path))

