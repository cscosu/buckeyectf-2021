guess_god
=====

This challenge consists of a C++ web application that allows you to upload and download files.

There is a 'decompress' option when you download files that uses a custom 'kylezip' compression
algorithm. This algorithm is vulnerable to memory corruption, but any corruption you can do is relative to a constant address (0x13371337000 or 0x42069000).

To run the decompression routine, the web server forks and then calls the library function. If the library function crashes, that sucks but the web server will stay up. Because forked processes inherit all of the parent's memory mappings, this gives us the ability to brute force the ASLR slide (if the decompression succeeds, we guessed correctly).

Because all downloads are mmap-d 'for performance' we can download a large file and a large mmap-d region will be created. We can brute force for the beginning/end of this region to break ASLR.

Inspired by: [https://googleprojectzero.blogspot.com/2020/01/remote-iphone-exploitation-part-2.html](https://googleprojectzero.blogspot.com/2020/01/remote-iphone-exploitation-part-2.html)
