// TC21: Missing parentheses in switch expression
#include <iostream>
using namespace std;

int main() {
    int choice = 2;
    switch choice {
        case 1:
            cout << "Choice 1" << endl;
            break;
        default:
            cout << "Default" << endl;
    }
    return 0;
}
