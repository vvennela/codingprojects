#include "Plugboard.h"
#include "common.h"
#include <string.h>


/*
void initPlugboard(struct plugboard* Plugboard) {
    for (int i = 0; i < MAX_SIZE; i++) {
        Plugboard->switches[i] = i;
    }
}

void switchPairs(struct plugboard* Plugboard, const char* pairs) {
    size_t length = strlen(pairs);
    for (size_t i = 0; i < length; i += 2) {
        char a = pairs[i];
        char b = pairs[i + 1];

        if (a >= 'A' && a <= 'Z' && b >= 'A' && b <= 'Z' && a != b) {
            Plugboard->switches[a - 'A'] = b - 'A';
            Plugboard->switches[b - 'A'] = a - 'A';
        }
    }
}

char usePlugboard(struct plugboard* Plugboard, char letter) {
    if (letter >= 'A' && letter <= 'Z') {
        return Plugboard->switches[letter - 'A'] + 'A';
    }
    else {
        return letter;
    }
}

char processInput(struct plugboard* Plugboard, int input) {
    char output = input + 'A';
    return usePlugboard(Plugboard, output);
} */
