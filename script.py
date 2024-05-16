__version__ = "0.2.3"

import pathlib
import argparse
import pyperclip as clipboard
import color
from color import paint


class ParserArgs(argparse.Namespace):
    end: str


parser = argparse.ArgumentParser(
    prog="Here",
    usage="Copy 'here' path to clipboard"
    )
parser.add_argument("-v", "--version",
                    action="version",
                    version=f"%(prog)s: v{__version__}")
parser.add_argument("end",
                    nargs="?",
                    default=".",
                    help="Relative path to join with current working directory path")
args = ParserArgs()
parser.parse_args(namespace=args)

absolute_path = (pathlib.Path
                 .cwd()
                 .joinpath(args.end)
                 .resolve())

print(paint("[Info]", color.AQUA),
      paint("Copying to clipboard", color.PINK) + paint(":", color.WHITE),
      paint(absolute_path, color.UNDERLINE + color.DARK_VIOLET))

clipboard.copy(str(absolute_path))
