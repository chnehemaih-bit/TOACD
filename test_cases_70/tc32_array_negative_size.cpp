// TC32: Negative dimension in array declaration
#include <iostream>
using namespace std;

int main() {
    int buffer[-5];
    return 0;
}
