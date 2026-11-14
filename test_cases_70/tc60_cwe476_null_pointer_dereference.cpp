// TC60: NULL Pointer Dereference (CWE-476)
// Vulnerability: Attempting to read or write through a nullptr
#include <iostream>
using namespace std;

int main() {
    int* bad_ptr = nullptr;
    *bad_ptr = 42;
    cout << "Deref: " << *bad_ptr << endl;
    return 0;
}
