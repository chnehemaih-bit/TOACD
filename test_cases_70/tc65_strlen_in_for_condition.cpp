// TC65: strlen() Recalculated in Loop Condition
// Benchmark: strlen() is O(n), making the entire loop O(n^2) instead of O(n)
#include <iostream>
#include <cstring>
using namespace std;

int main() {
    char text[] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
    int vowels = 0;
    for (int i = 0; i < strlen(text); i++) {
        char c = text[i];
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
            vowels++;
        }
    }
    cout << "Vowels: " << vowels << endl;
    return 0;
}
