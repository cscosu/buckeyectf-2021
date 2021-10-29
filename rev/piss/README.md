piss
====

Category: rev (really, revpwn)
Points: 500 (0 solves during CTF)

This is a series of two challenges, `piss_1` and `piss_2`

This challenge is a sort of syscall jail, but instead of using seccomp or something, it disassembles one basic block (more or less) at a time and modifies the code (even through libraries) so that syscalls
go through a filter function before being executed. Even if you jump to libc, the jail will modify the code in libraries based on the same rules. This creates a sort of 'jail' which you need to escape. 


