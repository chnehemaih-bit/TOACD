// TC46: Void function returning an expression value
#include <iostream>
using namespace std;

void displayMessage() {
    cout << "Processing..." << endl;
    return 42;
}

int main() {
    displayMessage();
    return 0;
}
