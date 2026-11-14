using namespace std;

// Test Case 5: Missing #include <iostream>
// Dev-C++ Expected Error: 'cout' was not declared in this scope; did you mean '#include <iostream>'?
int main() {
    int val = 100;
    cout << "Value output: " << val << endl;
    return 0;
}
