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

    def linux_supported(self):
        """
        Gets the extensions published by the Linux kernel

        Returns: List of extensions

        Raises:
            RiscvExtException: If the provided ISA string is invalid.
        """

        linux_6_14 = SortedList([
			'i', 'm', 'a', 'f', 'd', 'q', 'c', 'v', 'zicbom', 'zicboz',
			'ziccrse', 'zicntr', 'zicond', 'zicsr', 'zifencei',
			'zihintntl', 'zihintpause', 'zihpm', 'zimop', 'zabha', 'zacas',
			'zawrs', 'zfa', 'zfh', 'zfhmin', 'zca', 'zcb', 'zcd', 'zcf',
			'zcmop', 'zba', 'zbb', 'zbc', 'zbkb', 'zbkc', 'zbkx', 'zbs',
			'zk', 'zkn', 'zknd', 'zkne', 'zknh', 'zkr', 'zks', 'zkt',
			'zksed', 'zksh', 'ztso', 'zvbb', 'zvbc', 'zve32f', 'zve32x',
			'zve64d', 'zve64f', 'zve64x', 'zvfh', 'zvfhmin', 'zvkb', 'zvkg',
			'zvkn', 'zvknc', 'zvkned', 'zvkng', 'zvknha', 'zvknhb', 'zvks',
			'zvksc', 'zvksed', 'zvksh', 'zvksg', 'zvkt'
            ])
        self.add_implied_extensions(linux_6_14)

        return linux_6_14

    def rva23_required(self):
        """
        Gets the extensions required for RVA23

        Returns: List of extensions

        Raises:
            RiscvExtException: If the provided ISA string is invalid.
        """

        rva23 = SortedList({
			'i', 'm', 'a', 'f', 'd', 'c', 'b', 'v', 'zic64b',
			'zicbom', 'zicbop', 'zicboz', 'ziccamoa', 'ziccif', 'zicclsm',
			'ziccrse', 'zicntr', 'zicond', 'zicsr', 'zifencei',
			'zihintntl', 'zihintpause', 'zihpm', 'zimop', 'za64rs',
			'zawrs', 'zfa', 'zfbfmin', 'zfhmin', 'zcb', 'zcmop', 'zba',
			'zbb', 'zbs', 'zvbb', 'zvfhmin', 'zvkt', 'zkn', 'zkr', 'zkt'
            })
        self.add_implied_extensions(rva23)

        return rva23

    def rva23_to_check(self):
        """
        Gets the required RVA23 extensions published by the Linux kernel

        Returns: List of extensions

        Raises:
            RiscvExtException: If the provided ISA string is invalid.
        """

        linux = self.linux_supported()
        check = self.rva23_required()

        return SortedList(ext for ext in check if ext in linux)

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
            'a' : ['zaamo'],
            'f' : ['zicsr'],
            'd' : ['f'],
            'q' : ['d'],
            'v' : ['d'],
            'zfh' : ['zfhmin'],
        })

        shorthand = SortedDict({
            'b' : ['zba', 'zbb', 'zbs'],
            'g' : ['i', 'm', 'a', 'f', 'd', 'zicsr', 'zifencei'],
            'zk' : ['zkn', 'zkr', 'zkt'],
            'zkn' : ['zbkb', 'zbkc', 'zbkx', 'zkne', 'zknd', 'zknh'],
            'zks' : ['zbkb', 'zbkc', 'zbkx', 'zksed', 'zksh'],
            'zvkn' : ['zvkned', 'zvknhb', 'zvkb', 'zvkt'],
            'zvknc' : ['zvkn', 'zvbc'],
            'zvkng' : ['zvkn', 'zvkg'],
            'zvks' : ['zvksed', 'zvksh', 'zvkb', 'zvkt'],
            'zvksc' : ['zvks', 'zvbc'],
            'zvksg' : ['zvks', 'zvkg'],
        })

        # Add implied extensions
        update = True
        while update:
            update = False
            for extension in extensions:
                if extension in implies:
                    for implied in implies[extension]:
                        if implied not in extensions:
                            extensions.add(implied)
                            update = True
                if update:
                    break

        # Substitute shorthand extensions
        update = True
        while update:
            update = False
            for extension in extensions:
                if extension in shorthand:
                    for implied in shorthand[extension]:
                        if implied not in extensions:
                            extensions.add(implied)
                    extensions.remove(extension)
                    update = True
                    break


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

    @staticmethod
    def read_cpuinfo():
        """
        Gets the extensions listed in /proc/cpuinfo as common for all harts

        Returns: List of extensions

        Raises:
            RiscvExtException: If the ISA string is invalid or cannot be found
        """

        try:
            with open('/proc/cpuinfo', 'rb') as file:
                binary_content = file.read()
        except Exception as ex:
            raise RiscvExtensionException('Can\'t read /proc/cpuinfo') from ex

        lines = binary_content.decode('utf-8', errors='ignore').splitlines()
        for line in lines:
            match = re.match(r'isa\s*:\s*', line)
            if match:
                return RiscvExtensionAnalyzer(line[match.end():])

        raise RiscvExtensionException('No ISA information')

    @staticmethod
    def is_rva23_ready():
        """
        Check if the system is RVA23 ready

        Raises:
            RiscvExtException: If the system is not RVA23 ready
        """

        cpuinfo = RiscvExtensionAnalyzer.read_cpuinfo()
        check = cpuinfo.rva23_to_check()
        for ext in check:
            if ext not in cpuinfo.extensions:
                raise RiscvExtensionException(f'Missing extension {ext}')

    def __init__(self, isa_string):
        """
        Initializes a RiscvExtensionAnalyzer object with a given RISC-V ISA string.

        Args:
            isa_string (str): The RISC-V ISA string to analyze.

        Raises:
            RiscvExtException: If the provided ISA string is invalid.
        """

        isa_string = isa_string.lower()
        self.bitness, remainder = self.check_base_isa(isa_string)
        self.extensions = self.parse_isa_string(remainder)

def test_bitness():
    """
    Test bitness
    """
    actual = RiscvExtensionAnalyzer('RV32IMACZicsr_Zifencei').bitness
    expected = 32
    assert expected == actual

    actual = RiscvExtensionAnalyzer('rv64gcsv39').bitness
    expected = 64
    assert expected == actual

def test_extensions():
    """
    Test extensions
    """
    actual = RiscvExtensionAnalyzer('RV32IMACZicsr_Zifencei').extensions
    expected = SortedList(['a', 'c', 'i', 'm', 'zicsr', 'zifencei', 'zmmul'])
    assert expected == actual

    actual = RiscvExtensionAnalyzer('RV32IMACZicsr_Zifencei').bitness
    expected = 32
    assert expected == actual

    actual = RiscvExtensionAnalyzer(
            'rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_'
            'zicsr2p0_zifencei2p0_zmmul1p0_zaamo1p0_zalrsc1p0').extensions
    expected = SortedList(['a', 'c', 'd', 'f', 'i', 'm', 'zaamo', 'zalrsc',
                            'zicsr', 'zifencei', 'zmmul'])
    assert expected == actual

    actual = RiscvExtensionAnalyzer('rv64gcsv39').extensions
    expected = SortedList(['a', 'c', 'd', 'f', 'g', 'i', 'm', 'sv39',
                            'zicsr', 'zifencei', 'zmmul'])
    assert expected == actual

if __name__ == '__main__':
    try:
        RiscvExtensionAnalyzer.is_rva23_ready()
        print('The system is RVA23 read')
        sys.exit(0)
    except RiscvExtensionException as ex:
        print(ex)
        sys.exit(1)
