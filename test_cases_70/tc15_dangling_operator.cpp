// TC15: Dangling operator missing right-hand operand
#include <iostream>
using namespace std;

int main() {
    int a = 10;
    int b = a + ;
    cout << b << endl;
    return 0;
}
