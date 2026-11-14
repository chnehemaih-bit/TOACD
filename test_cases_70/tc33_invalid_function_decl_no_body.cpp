// TC33: Function definition missing body braces
#include <iostream>
using namespace std;

int add(int a, int b)
    return a + b;

int main() {
    cout << add(3, 4) << endl;
    return 0;
}
