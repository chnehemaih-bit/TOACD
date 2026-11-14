#include <iostream>
using namespace std;

// Test Case 4: Misspelled Keywords (itn -> int, prinft -> printf, reutrn -> return)
// Dev-C++ Expected Error: 'itn' was not declared in this scope; did you mean 'int'?
int main() {
    itn count = 5;
    prinft("Count is %d\n", count);
    reutrn 0;
}
