// TC49: Invoking non-callable primitive as a function
#include <iostream>
using namespace std;

int main() {
    int active_session = 10;
    active_session();
    return 0;
}
