#include <iostream>
using namespace std;

int main() {
    int* ptr = new int[100];

    ptr[0] = 50;

    cout << ptr[0];

    return 0;
}
