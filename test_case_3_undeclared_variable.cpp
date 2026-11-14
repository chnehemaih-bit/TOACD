#include <iostream>
using namespace std;

// Test Case 3: Undeclared Variable
// Dev-C++ Expected Error: 'result' was not declared in this scope (line 9)
int main() {
    int a = 15;
    int b = 25;
    result = a + b;
    cout << "Calculation Result: " << result << endl;
    return 0;
}
