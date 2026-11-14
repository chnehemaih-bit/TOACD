// TC29: Conflicting type specifiers
#include <iostream>
using namespace std;

int main() {
    int float measurement = 45.67;
    cout << "Measurement: " << measurement << endl;
    return 0;
}
