#include <iostream>
using namespace std;

// Test Case 2: Unmatched Brace (Missing Closing Brace in if-block)
// Dev-C++ Expected Error: expected '}' at end of input
int main() {
    int x = 42;
    if (x > 0) {
        cout << "Positive value: " << x << endl;
    return 0;
}
