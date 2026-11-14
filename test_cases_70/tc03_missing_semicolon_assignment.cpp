// TC03: Missing semicolon in assignment expression
#include <iostream>
using namespace std;

int main() {
    int count = 10;
    count = count + 25
    cout << "Updated count: " << count << endl;
    return 0;
}
