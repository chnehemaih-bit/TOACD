// TC02: Missing semicolon after return statement
#include <iostream>
using namespace std;

int calculateTax(int income) {
    int rate = 15;
    return income * rate / 100
}

int main() {
    cout << "Tax: " << calculateTax(50000) << endl;
    return 0;
}
