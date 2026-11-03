#include <iostream>
using namespace std;

class MyClass
public:
    int x;
    void method() {
        cout << "Hello";
    }
};

int main() {
    MyClass obj;
    obj.x = 5;
    return 0;
}