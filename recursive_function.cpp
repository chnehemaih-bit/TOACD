#include <iostream>
using namespace std;

int factorial(int n) {
    return n * factorial(n - 1);
}

int main() {
    cout << factorial(5);
    return 0;
}
