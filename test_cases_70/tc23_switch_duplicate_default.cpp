// TC23: Multiple default labels in switch
#include <iostream>
using namespace std;

int main() {
    int mode = 0;
    switch (mode) {
        case 1:
            cout << "Mode 1" << endl;
            break;
        default:
            cout << "Primary Default" << endl;
            break;
        default:
            cout << "Duplicate Default" << endl;
            break;
    }
    return 0;
}
