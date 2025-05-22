#!/bin/python3
"""
riscv_extension_analyzer

This module provides functionality for analyzing and parsing RISC-V extension
strings.

Key Features:
- Validate RISC-V extension strings to ensure they conform to the expected
  format.
- Parse extension strings to extract base ISA information and supported
  extensions.

Author: Heinrich Schuchardt
Version: 0.0.1
"""

import sys
import re
from sortedcontainers import SortedDict, SortedList

class RiscvExtensionException(RuntimeError):
    """
    Exception raised for errors related to RISC-V extensions.

    This exception is a subclass of RuntimeError and is used to indicate
    issues specifically related to the RISC-V instruction set architecture
    extensions.

    Attributes:
        message (str): A description of the error.
    """

    def __init__(self, message):
        super().__init__(message)


class RiscvExtensionAnalyzer:
    """
    RiscvExtensionAnalyzer

    This class provides functionality to analyze and parse RISC-V extension
    strings.
    """

    CANONICAL_ORDER = 'imafdqlcbkjtpvh'

    def check_base_isa(self, isa_string):
        """
        Checks the base instruction set architecture (ISA) provided by a
        RISC-V extension string.

        Args:
            isa_string (str): The RISC-V extension string to analyze.

        Returns:
            bitness (int): Bitness of base ISA.
            remainder (str): Remaining ISA string.

        Raises:
            RiscvExtensionException:
            If the string does not start with a valid base ISA identifier.
        """

        base_isas = {
            'rv128': 128,
            'rv64':  64,
            'rv32':  32}

        bitness = None
        for key, value in base_isas.items():
            if isa_string.startswith(key):
                bitness = value
                remainder = isa_string[len(key):]
                break

        if bitness is None:
            raise RiscvExtensionException('Invalid base ISA')

        return bitness, remainder

    def add_implied_extensions(self, extensions):
        """
        Adds implied extensions

        Args:
            extensions: iterable of extensions
        """

        implies = SortedDict({
            'm' : ['zmmul'],
            'f' : ['zicsr'],
            'd' : ['f'],
            'g' : ['i', 'm', 'a', 'f', 'd', 'zicsr', 'zifencei'],
            'q' : ['d'],
            'b' : ['zba', 'zbb', 'zbs'],
            'v' : ['d'],
        })
        update = True

        while update:
            update = False
            for extension in extensions:
                if extension in implies:
                    for implied in implies[extension]:
                        if implied not in extensions:
                            extensions.add(implied)
                            update = True


    def parse_isa_string(self, isa_string):
        """
        Parse RISC-V ISA string

        args:
            isa_string: ISA string without base ISA (e.g. rv64)

        Raises:
            RiscvExtException: If the provided ISA string is invalid.
        """
        multi_character = False

        extensions = SortedList()

        while len(isa_string) > 0:
            if isa_string.startswith('_'):
                isa_string = isa_string[1:]
                if not isa_string:
                    raise RiscvExtensionException('Missing extension')
            elif multi_character:
                raise RiscvExtensionException('Expecting underscore')
            if isa_string[0] in 'sxz':
                multi_character = True
            if multi_character:
                match = re.match(r'^[^_]+', isa_string)
            else:
                match = re.match(r'^\D\d+p\d+|\D\d+|\D', isa_string)
            if not match:
                raise RiscvExtensionException('Expecting extension')
            extension = match.group()
            isa_string = isa_string[match.end():]
            # These extensions are not versioned.
            if extension not in {'sv32', 'sv39', 'sv48', 'sv59'}:
                # Check for version number.
                match = re.search(r'\d+p\d+$', extension)
                if not match:
                    match = re.search(r'\d+$', extension)
                if match:
                    # version = extension[match.start()]
                    extension = extension[:match.start()]
            if not extension:
                raise RiscvExtensionException('Zero length extension')

            extensions.add(extension)

        self.add_implied_extensions(extensions)

        return extensions

    def __init__(self, isa_string):
        """
        Initializes a RiscvExtensionAnalyzer objectwith a given RISC-V ISA string.

        Args:
            isa_string (str): The RISC-V ISA string to analyze.

        Raises:
            RiscvExtException: If the provided ISA string is invalid.
        """

        isa_string = isa_string.lower()
        bitness, remainder = self.check_base_isa(isa_string)
        extensions = self.parse_isa_string(remainder)
        print(f'{bitness}')
        print(extensions)

def test_parse():
    """
    Test strings:

    RV32IMACZicsr_Zifencei
    """

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ARG_STRING = sys.argv[1]
    else:
        ARG_STRING = (
            'rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_'
            'zicsr2p0_zifencei2p0_zmmul1p0_zaamo1p0_zalrsc1p0')

    ext = RiscvExtensionAnalyzer(ARG_STRING)
