// TC13: Unterminated string literal in streaming statement
#include <iostream>
using namespace std;

int main() {
    string msg = "Compiler Diagnostics active;
    cout << msg << endl;
    return 0;
}
