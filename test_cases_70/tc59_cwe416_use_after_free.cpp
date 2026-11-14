// TC59: Use After Free Vulnerability (CWE-416)
// Vulnerability: Pointer is dereferenced after its heap memory was freed
#include <iostream>
using namespace std;

int main() {
    int* ptr = new int(100);
    delete ptr;
    // Dangerous write after delete
    *ptr = 200;
    cout << "Val: " << *ptr << endl;
    return 0;
}
