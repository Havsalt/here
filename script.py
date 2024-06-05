__version__ = "0.2.7"

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
    folder_mode: bool


parser = argparse.ArgumentParser(
    prog="here",
    usage="Copy 'here' path to clipboard"
    )
parser.add_argument("-v", "--version",
                    action="version",
                    version=f"%(prog)s: v{__version__}")
parser.add_argument("-f", "--folder",
                    action="store_true",
                    dest="folder_mode")
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
    if args.end == ".":
        if not args.silent:
            print(paint("[Error]", color.CRIMSON),
                  paint("Cannot search for", color.GRAY),
                  paint("'.'", color.WHITE)
                  + paint(". Argument", color.GRAY),
                  paint("end", color.WHITE),
                  paint("required", color.GRAY))
            print(paint("[Info]", color.SEA_GREEN),
                  paint("Caused by flag", color.GRAY),
                  paint("-w", color.WHITE)
                  + paint("/", color.GRAY)
                  + paint("--from-where", color.WHITE))
        exit(1) # error code
    result = subprocess.run(["where", args.end],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    if result.returncode != 0:
        if not args.silent:
            print(paint("[Error]", color.CRIMSON),
                  paint("Cold not find", color.GRAY),
                  paint(args.end, color.WHITE))
            print(paint("[Info]", color.SEA_GREEN),
                  paint("Caused by flag", color.GRAY),
                  paint("-w", color.WHITE)
                  + paint("/", color.GRAY)
                  + paint("--from-where", color.WHITE))
        exit(2)
    location = result.stdout.rstrip("\n ")
    absolute_path = (
        pathlib.Path(location)
        .resolve()
    )
else:
    absolute_path = (
        pathlib.Path
        .cwd()
        .joinpath(args.end)
        .resolve()
    )
if args.folder_mode:
    if absolute_path.is_file():
        absolute_path = absolute_path.parent

if not args.silent:
    if args.verbose:
        print(paint("[Info]", color.SEA_GREEN),
              paint("Copying to clipboard", color.GRAY) + paint(":", color.WHITE),
              paint(absolute_path, color.UNDERLINE + color.SALMON))
    else:
        print(paint(absolute_path, color.SALMON))

clipboard.copy(str(absolute_path))

