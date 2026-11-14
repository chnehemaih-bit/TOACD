// TC52: Stack Buffer Overflow via strcpy() (CWE-121)
// Vulnerability: strcpy() lacks destination boundary checks
#include <iostream>
#include <cstring>
using namespace std;

void copyName(const char* input) {
    char dest[12];
    strcpy(dest, input);
    cout << "Stored name: " << dest << endl;
}

int main() {
    const char* long_str = "ThisStringIsFarTooLongForTheBuffer";
    copyName(long_str);
    return 0;
}
