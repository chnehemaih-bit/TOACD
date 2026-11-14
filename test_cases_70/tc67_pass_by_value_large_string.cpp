// TC67: Unnecessary Deep Copy via Pass-by-Value
// Benchmark: Passing std::string by value invokes heap copy; use 'const string&'
#include <iostream>
#include <string>
using namespace std;

int countSpaces(string text) {
    int count = 0;
    for (char c : text) {
        if (c == ' ') count++;
    }
    return count;
}

int main() {
    string large_document(100000, 'x');
    cout << "Spaces: " << countSpaces(large_document) << endl;
    return 0;
}
