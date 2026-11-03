#include <iostream>

namespace MyNamespace
    int x = 5;
    void func() {
        std::cout << "Hello";
    }
}

int main() {
    MyNamespace::func();
    return 0;
}