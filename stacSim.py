#!/opt/homebrew/bin/python3
"""
STAC Interpreter

Encapsulates VM state in a class and eliminates global variable dependencies while
safely supporting dynamic Python expressions used in STAC instructions.

--

author: Allan Sioson
asioson@ateneo.edu

Note: This interpreter is meant to be used to run the output of student submitted
translators as requirement in CSCI202.

"""

import sys


class VirtualMachine:
    def __init__(self):
        # VM Memory and Configuration
        self.mem = []
        self.sym_tab = {}
        self.mem_size = 0
        self.code_size = 0

        # Registers
        self.ip = 0  # Instruction Pointer
        self.sp = 0  # Stack Pointer
        self.bp = 0  # Base Pointer
        self.ac = 0  # Accumulator

    def iread(self) -> int:
        """Helper method exposed to STAC instructions via execution scope."""
        data = input().split()
        return int(data[0]) if data else 0

    def load_program(self, filename: str) -> bool:
        """Parses the input .stac file into system memory state."""
        self.sym_tab = {}
        ismem, iscode, issymtab = False, False, False
        i = 0

        try:
            with open(filename, "r") as file:
                content = file.read()
        except FileNotFoundError:
            print(f"error: cannot read {filename}", file=sys.stderr)
            return False

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue

            if line == "[code]":
                ismem, iscode, issymtab = False, True, False
            elif line == "[mem]":
                ismem, iscode, issymtab = True, False, False
            elif line == "[symTab]":
                ismem, iscode, issymtab = False, False, True
            else:
                if ismem:
                    name, size = line.split()
                    val = int(size)
                    if name == "memSize":
                        self.mem_size = val
                        self.mem = [None for _ in range(self.mem_size)]
                    elif name == "codeSize":
                        self.code_size = val
                elif iscode:
                    self.mem[i] = list(line.split())
                    i += 1
                elif issymtab:
                    name, value = line.split()
                    self.sym_tab[name] = value

        return True

    def resolve_symbols(self):
        """Replaces symbolic identifiers in bytecode with resolved values."""
        for i in range(self.code_size):
            if isinstance(self.mem[i], list):
                for k, v in self.sym_tab.items():
                    for j in range(len(self.mem[i])):
                        if self.mem[i][j] == k:
                            self.mem[i][j] = str(v)

    def show_final_code(self):
        """Prints loaded state for debugging."""
        print("[mem]")
        print("memSize", self.mem_size)
        print("codeSize", self.code_size)
        print("\n[code]")
        for i in range(self.code_size):
            line = self.mem[i]
            print(i, " ".join(line) if isinstance(line, list) else line)
        print("\n[symTab]")
        for k, v in self.sym_tab.items():
            print(k, v)

    def run(self):
        """Executes bytecode instructions within an isolated scope."""
        if "main" not in self.sym_tab:
            print("error: 'main' symbol not found in symbol table", file=sys.stderr)
            return

        # Initialize registers
        self.ip = int(self.sym_tab["main"])
        self.sp = self.mem_size
        self.bp = 0
        self.ac = 0

        while True:
            cmd = " ".join(self.mem[self.ip])
            if cmd == "halt":
                break

            oldip = self.ip

            # Build execution environment mapped to instance properties
            execution_scope = {
                "mem": self.mem,
                "ip": self.ip,
                "sp": self.sp,
                "bp": self.bp,
                "ac": self.ac,
                "memSize": self.mem_size,
                "codeSize": self.code_size,
                "iread": self.iread,
            }

            # Execute instruction cleanly without relying on global script state
            exec(cmd, execution_scope)

            # Sync registers back to VM instance after step execution
            self.ip = execution_scope["ip"]
            self.sp = execution_scope["sp"]
            self.bp = execution_scope["bp"]
            self.ac = execution_scope["ac"]

            # Advance instruction pointer if untouched by jump instructions
            if oldip == self.ip:
                self.ip += 1


def main():
    show_code = False
    args = sys.argv[1:]

    if len(args) == 1:
        filename = args[0]
    elif len(args) == 2 and args[0] == "-code":
        show_code = True
        filename = args[1]
    else:
        print(f"usage: {sys.argv[0]} [-code] prog.stac")
        return

    vm = VirtualMachine()
    if vm.load_program(filename):
        vm.resolve_symbols()
        if show_code:
            vm.show_final_code()
        else:
            vm.run()


if __name__ == "__main__":
    main()
