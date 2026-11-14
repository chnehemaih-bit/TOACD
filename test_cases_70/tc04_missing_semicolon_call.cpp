// TC04: Missing semicolon after function call
#include <iostream>
using namespace std;

void logMessage() {
    cout << "System operational" << endl;
}

int main() {
    logMessage()
    return 0;
}
