// TC58: Integer Overflow / Wraparound (CWE-190)
// Vulnerability: Multiplication of large 32-bit integers without overflow detection
#include <iostream>
using namespace std;

int main() {
    int max_val = 2147483640;
    int multiplier = 100;
    int result = max_val * multiplier;
    cout << "Overflow result: " << result << endl;
    return 0;
}
