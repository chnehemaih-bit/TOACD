// TC51: Buffer Overflow via gets() (CWE-120 / CWE-242)
// Vulnerability: gets() performs no bounds checking on input buffer
#include <iostream>
#include <cstdio>
using namespace std;

void readUserInput() {
    char username[16];
    cout << "Enter username: ";
    gets(username);
    cout << "Hello, " << username << endl;
}

int main() {
    readUserInput();
    return 0;
}
