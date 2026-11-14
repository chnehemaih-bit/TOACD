// TC34: Function parameter missing type
#include <iostream>
using namespace std;

int multiply(a, int b) {
    return a * b;
}

int main() {
    cout << multiply(5, 6) << endl;
    return 0;
}
