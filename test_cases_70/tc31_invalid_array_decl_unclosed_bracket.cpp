// TC31: Missing closing bracket in array declaration
#include <iostream>
using namespace std;

int main() {
    int numbers[10;
    numbers[0] = 5;
    cout << numbers[0] << endl;
    return 0;
}
