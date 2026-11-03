#include <iostream>
using namespace std;

int main() {
    int x = 1;
    switch (x) {
        case 1:
            cout << "One"<<endl;
        case 2:
            cout << "Two"<<endl;
            break;
        default:
            cout << "Default"<<endl;
    }
    return 0;
}