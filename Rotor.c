#include "Rotor.h"
#include "common.h"
#include <string.h>
#include <stdbool.h>
/*

void initRotor(struct Rotor *rotor, const char *wiring, int ring, int init) {
    strcpy(rotor->left, LETTERS);

    size_t wiringLength = strlen(wiring);
    strncpy(rotor->right, wiring, wiringLength);
    rotor->right[wiringLength] = '\0';

    rotor->turnover = wiring[wiringLength - 1];

    for (int i = 0; i < ring; i++) {
        rotor->left[i] = 'A' + (rotor->left[i] - 'A' + 1);
        rotor->right[i] = 'A' + (rotor->right[i] - 'A' + 1);
    }

    for (int i = 0; i < init; i++) {
        char tempRotor = rotor->left[0];
        memmove(rotor->left, rotor->left + 1, MAX_SIZE - 1);
        rotor->left[MAX_SIZE - 1] = tempRotor;

        tempRotor = rotor->right[0];
        memmove(rotor->right, rotor->right + 1, MAX_SIZE - 1);
        rotor->right[MAX_SIZE - 1] = tempRotor;
    }
}


int forward(const struct Rotor *rotor, int input) {
    char letter = rotor -> right[input % MAX_SIZE];
    input = strchr(rotor -> left, letter) - rotor -> left;
    return input;

}

int backward(const struct Rotor *rotor, int input) {
    char letter = rotor -> left[input % MAX_SIZE];
    input = strchr(rotor -> right, letter) - rotor -> right;
    return input;
}

void rotate(struct Rotor *rotor, int n, bool forward) {
    for (int i = 0; i < n; i++) {
        if (forward) {
            char temp = rotor->left[0];
            memmove(rotor->left, rotor->left + 1, MAX_SIZE - 1);
            rotor->left[MAX_SIZE - 1] = temp;

            temp = rotor->right[0];
            memmove(rotor->right, rotor->right + 1, MAX_SIZE - 1);
            rotor->right[MAX_SIZE - 1] = temp;
        } else {
            char temp = rotor->left[MAX_SIZE - 1];
            memmove(rotor->left + 1, rotor->left, MAX_SIZE - 1);
            rotor->left[0] = temp;

            temp = rotor->right[MAX_SIZE - 1];
            memmove(rotor->right + 1, rotor->right, MAX_SIZE - 1);
            rotor->right[0] = temp;
        }
    }
}

void rotateLetter(struct Rotor *rotor, char letter) {
    const char* lookup = LETTERS;
    char* result = strchr(lookup, letter);
    int n = result - lookup;
    rotate(rotor, n, true);
}

void setRing(struct Rotor *rotor, int n) {
    char turnover = rotor -> turnover;
    int notch = strchr(LETTERS, turnover) - LETTERS;
    rotate(rotor, n-1, false);
    turnover = LETTERS[(notch - n + 26) % 26];
} */
