#include <stdint.h>
int main(int argc, char *argv[])
{
    uint8_t x = 5;
    uint8_t y = 0;
    if (x == 5) {
        y = 1;
    } else {
        y = 2;
    }

    return 0;
}
