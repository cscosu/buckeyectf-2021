#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void hex_print(char* buf, int n) {
    for (int i = 0; i < n; ++i) {
        if (i > 0 && i % 8 == 0) {
            printf("\n");
        }
        printf("%02x ", (unsigned char)buf[i]);
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    char* buf;
    buf = malloc(256);
    strcpy(buf, "buckeye{hello_please_read_this}");
    free(buf);

    hex_print(buf, 256);
    printf("---\n");

    buf = malloc(256);

    hex_print(buf, 256);

    printf("%s\n", buf);
    free(buf);

    return 0;
}
