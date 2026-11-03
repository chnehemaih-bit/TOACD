#include <iostream>
using namespace std;

unsigned int decrypt(unsigned int num, unsigned int r {
    return num + r;
}

int main() {
    cout << decrypt(2, 3);
    return 0;
}
