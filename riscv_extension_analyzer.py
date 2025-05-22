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
            raise RiscvExtensionException('Invalid start')

        return bitness, remainder

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
        print(f'{bitness}, {remainder}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ARG_STRING = sys.argv[1]
    else:
        ARG_STRING = 'rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0_zmmul1p0_zaamo1p0_zalrsc1p0'

    ext = RiscvExtensionAnalyzer(ARG_STRING)
