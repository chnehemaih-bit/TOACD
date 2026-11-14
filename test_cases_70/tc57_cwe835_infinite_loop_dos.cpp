// TC57: Infinite Loop / Denial of Service (CWE-835)
// Vulnerability: Unbounded loop with constant true condition and no break statement
#include <iostream>
using namespace std;

int main() {
    int heart_beat = 0;
    while (true) {
        heart_beat++;
        // Missing termination condition or break
    }
    return 0;
}
