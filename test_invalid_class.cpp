#include <iostream>
using namespace std;

class MyClass
{
public:
    int value;
};

int main() {
    MyClass obj;
    obj.value = 5;
    cout << obj.value << endl;
    return 0;
}
