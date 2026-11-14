#include <iostream>
using namespace std;

// Test Case 1: Missing Semicolon
// Dev-C++ Expected Error: expected ';' before 'int' token (line 9)
int main() {
    int a = 10
    int b = 20;
    cout << "Sum: " << (a + b) << endl;
    return 0;
}
