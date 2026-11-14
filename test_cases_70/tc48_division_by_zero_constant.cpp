// TC48: Division by zero constant (CWE-369)
#include <iostream>
using namespace std;

int main() {
    int numerator = 100;
    int quotient = numerator / 0;
    cout << "Quotient: " << quotient << endl;
    return 0;
}
