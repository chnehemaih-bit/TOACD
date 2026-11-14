// TC22: Switch case missing colon
#include <iostream>
using namespace std;

int main() {
    int option = 1;
    switch (option) {
        case 1
            cout << "Option 1 Selected" << endl;
            break;
        default:
            cout << "Other" << endl;
    }
    return 0;
}
