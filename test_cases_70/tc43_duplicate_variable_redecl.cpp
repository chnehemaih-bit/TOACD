// TC43: Redeclaration of variable in the same scope
#include <iostream>
using namespace std;

int main() {
    int port = 8080;
    int port = 9000;
    cout << "Port: " << port << endl;
    return 0;
}
