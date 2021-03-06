Challenge file is a program for TI-83+ family calculators. There are 2 types of programs: those written in TI-Basic and those written in assembly (architecture is z80). This challenge is written in assembly and compiled with spasm-ng.

From a competitor's perspective, they should already know that .8xp files are for ti calculators based on the "BASIC" challenge. Based on the challenge name and the fact that they can't edit the program on the calculator, participants should be able to determine that this is an assembly program that they need to reverse. 

.8xp files contain the flat binary wrapped in some extra data. Part of this wrapping tells the participants the file was generated by spasm. There are a few ways participants can obtain the flat binary:
- write a barebones z80 asm program, compile to .bin and to .8xp with spasm-ng, see where the flat binary is present in their .8xp, use that to determine the flat binary in the provided .8xp
- use https://asmtools.omnimaga.org/
- use any number of other hacked together scripts from calculator forums
- read online sources about the .8xp format, write their own parser to rip out the flat binary

once the flat binary has been obtained, participants have a few options for the disassembly/static analysis:
- a standard modern disassembly tool where they specify the architecture and load address. note that these will miss a lot of TI-specific information and might have issues with the plain z80 disassembly! I tested with:
    - Ghidra
    - rizin
    - didn't test with IDA but there's a good forum post about using it here https://www.omnimaga.org/asm-language/ida-pro/ and here https://retrocomputing.stackexchange.com/questions/20257/good-z80-disassembler-decompiler-on-modern-equipment
    - online disassembler (ODA) - supports z80 but misses romcalls, https://onlinedisassembler.com/odaweb/
- a generic z80 disassembler - many can be found via a google search. also will miss a lot of TI-specific information but will probably be spot in with the z80 disassembly. I found:
    - "dZ80 2.0" - sounds like it is z80 generic (not TI specific) so probably misses TI routines, http://www.inkland.org.uk/dz80/
    - "Z80Disasm" MetaCPAN - z80 generic, https://metacpan.org/pod/CPU::Z80::Disassembler
    - "Z80Disasm" TRS-80 - z80 generic, http://www.trs-80emulators.com/z80disasm/
    - "Z80DisAssembler" - z80 generic but mentions RST opcodes, https://github.com/sarnau/Z80DisAssembler
    - "YAZD/YAZA" - https://github.com/toptensoftware/yazd
    - z80dasm - https://linux.die.net/man/1/z80dasm
    - tzxtools - great documentation! https://shred.zone/cilla/page/426/z80-disassembler.html
- a z80 disassembler intended specifically for ti calculators - many can be found on calculator forums or via a google search. the output from these should be a lot prettier and closer to the original source than other options. I found:
    - "Z80Disassembler v1.0" - based on the readme sounds like it is probably smart enough to show TI routines, https://www.ticalc.org/archives/files/fileinfo/349/34903.html
    - on-calculator disassembler so you can monkeypatch stuff, https://www.ticalc.org/archives/files/fileinfo/472/47293.html

participants likely won't have seen z80 before. thankfully, z80 is really simple (the first assembly language I learned) and there are plenty of great z80 assembly tutorials on the internet that participants should be able to utilize, e.g. https://tutorials.eeems.ca/ASMin28Days/lesson/toc.html. beyond understanding the actual assembly, a proper resource should help the participants learn additional information that is crucial to cleaning up the assembly:
- the load address/entry point is 0x9d95
- when writing assembly, developers make use of a "ti83plus.inc" file which contains a bunch of names for constant addresses in the TI calculator memory layout, e.g. 0x844B is curRow (the row of the current text position on the screen) and _PutC (an OS routine) is at 0x4504
- the modern disassembly tools that I tested with decompile the bcalls wrong and show them as a single-byte rst instruction. participants could discover this by reading the ti83plus.inc file which shows that bcalls are rst 28 instructions followed by a dword of operands, or by setting up their own test compilation environment (remember that participants have the name of the assembler I used from the .8x0 file!) and noticing how their bcalls show up

once the participants discover the above, they should be able to make significant progress defining code sections, replacing constant names, etc. to get much closer to the original source code and start understanding what the code does. from there, this is a standard reversing chall where you need to figure out what's happening in order to determine valid input that will result in the flag. in addition to the above-mentioned static analysis tools, tilem is a calculator emulator which offers a debug mode that shows register state, flags, memory state, and a decompilation view which is really nice (properly parses bcalls and other ti-os constants, much better than ghidra! but doesn't handle non-code sections very well - you can't tell it to just show the hex). also since ti assembly programs are all loaded at the same address it's super easy to set a breakpoint at 0x9d95, run the program, and break right at the entry point.

TI-83+ memory regions are RWX, so I made the code self-modifying. by breaking in the disassembler after the first djnz they should be able to get the decoded rest of the binary. from there it's just reversing to see that it takes your input, performs a couple rounds of substitutions and a modified caesar cipher, then compares that to a constant value. the computations are reversable so you can write a solve script (like the one in the solve folder) which calculates the input that reaches the code outputting "CORRECT". that input is the flag

things I can choose to provide to the participants or not:
- .8xp program
- ROM file to emulate the calculator
- link to learn z80 assembly in 28 days
- link to ti83plus.inc file (the one included in this repo is from https://www.ticalc.org/archives/files/fileinfo/243/24319.html as recommended by https://en.wikibooks.org/wiki/TI_83_Plus_Assembly/What_you_need)
- link to z80 or ti-specific disassembler which will do a better job than ghidra/rizin/ida/binja
- link to tilem
- original source
