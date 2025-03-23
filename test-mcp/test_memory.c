/**
 * Test file for memory management
 */
#include <stdio.h>
#include <stdlib.h>

// Missing memory management
void test_memory_leak() {
    char* buffer = malloc(100);
    // No free
}

int main() {
    printf("Testing memory management\n");
    test_memory_leak();
    return 0;
}
