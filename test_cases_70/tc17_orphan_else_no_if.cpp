// TC17: Orphan else statement without if
#include <iostream>
using namespace std;

int main() {
    int code = 404;
    else {
        cout << "Unknown state" << endl;
    }
    return 0;
}
