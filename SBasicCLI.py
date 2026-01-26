import argparse

from BasicInterpreter import BasicInterpreter


def main():
    parser = argparse.ArgumentParser(
                    prog='SBasic',
                    description='Sinclair-Spectrum-alike BASIC Interpreter',
                    epilog='This is not a Sinclair Spectrum emulator, but just a programming tool that resembles how programming was donde these days.')

    parser.add_argument("filepath", help="Old-fashioned BASIC program file")

    args = parser.parse_args()

    if not args.filepath:
        parser.print_help()
        return

    with open(args.filepath) as file:
        program = file.readlines()

    interpreter = BasicInterpreter()
    interpreter.load(program)
    interpreter.run()


if __name__ == "__main__":
    main()
