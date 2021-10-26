guess_god
======

I may choose to do a more detailed write-up later, but here's the short version.

NOTE: The exploit is not 100% reliable and you may have to run it 2-3 times to get the flag

## The bug

The kylezip compression library has a `do_decompress` function which is missing bounds checks, allowing you to read/write data from arbitrary addresses:

```
case 2: {
    // Seek
    uint64_t off = *(uint64_t*)(&in[cur]);
    cur += sizeof(off);
    out += off;
    break;
}
case 3: {
    // Copy some previously written bytes
    uint64_t off = *(uint64_t*)(&in[cur]);
    cur += sizeof(off);
    uint64_t count = *(uint64_t*)(&in[cur]);
    cur += sizeof(off);

    memcpy(out, out-off, count);
    out += count;
    break;
}
```

Because the offsets are 64-bit, we have complete control over the arguments to memcpy. We can copy memory into `out` which will get written to the decompressed file and returned from the HTTP request, allowing us to leak arbitrary memory.
Or, we can seek to an arbitrary address and write arbitrary bytes by uploading a carefully crafted compressed file.

The primary challenge here is breaking ASLR. Since `in` is mmap-d at `0x42069000000` and `out` is mmap-d at `0x13371337000`, we can't do any sort of relative write. We need to know the absolute address of where we want to write.

## Overview of exploitation

Just as Google Project Zero did in their [iOS exploitation blog post](https://googleprojectzero.blogspot.com/2020/01/remote-iphone-exploitation-part-2.html), we can break ASLR
in two steps:

1. Linear search to find **some address** in our large mmap-d segment. This is the slowest part of the solution.

    My solution creates a mmap-d region of size 1 * (10**9) (about 1GB)

    My solution searches 0x7f0000000000 - 0x7fffffffffff, which is around 1TB. This means it will take us about 500 guesses on average in our linear search. Remote is plenty fast for this.

    (note: occasionally we will get unlucky, and we will find an address not in our large mmap-d segment. so not 100% reliable)

2. Binary search to find the beginning of the large mmap-d segment. Note you have to search for the beginning, because the end is bordered by other accessible memory.

After breaking ASLR, you have a arbitrary write so you have a lot of options. Presumably there's an easy way to just overwrite something in libc or GOT, but I couldn't figure it out so I went for something different. (I'll leave the person who solved it to explain their technique)

I noticed (in GDB) that this application was spawning extra threads to handle requests. The
stacks for these threads are at a constant offset from the end of the libraries -- we can corrupt the stack! Thus, I chose to ROP to call `system("cat flag.txt")`. 


