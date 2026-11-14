// TC27: Invalid assignment with arithmetic expression on LHS
#include <iostream>
using namespace std;

int main() {
    int x = 10, y = 20;
    x + y = 30;
    cout << "Sum: " << x + y << endl;
    return 0;
}
