#include "Enigma.h"
#include "EnigmaImpl.h"
#include "Plugboard.c"
#include "Reflector.c"
#include "Rotor.c"

struct Rotor {
    char left[MAX_SIZE+1];
    char right[MAX_SIZE+1];
    char turnover;
};

struct reflector {
    char left[MAX_SIZE];
    char right[MAX_SIZE];
};

struct plugboard {
    int switches[MAX_SIZE];
};

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
}

void initReflector(struct reflector* reflector, const char* wiring) {
    for (int i = 0; i < 26; i++) {
        reflector->right[i] = wiring[i];
        reflector->left[i] = i + 65;
    }
}

int reflecting(struct reflector* reflector, int input) {
    int letter = reflector->right[input];
    input = reflector -> left[letter - 65] - 65;
    return input;
}



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
}



Enigma *new_Enigma(size_t num_rotors, const char **rotors, size_t *rings,
                   size_t *inits, const char *reflector, size_t num_pairs,
                   const char *pairs)
{
    Enigma *enigma = malloc(sizeof(Enigma));

    if (enigma == NULL) {
        return NULL;
    }

    enigma->rotors = malloc(num_rotors * sizeof(const char *));
    if (enigma->rotors == NULL) {
        free(enigma);
        return NULL;
    }

    enigma->num_rotors = num_rotors;

    enigma->rings = malloc(num_rotors * sizeof(size_t));
    if (enigma->rings == NULL) {
        free(enigma->rotors);
        free(enigma);
        return NULL;
    }

    enigma->inits = malloc(num_rotors * sizeof(size_t));
    if (enigma->inits == NULL) {
        free(enigma->rings);
        free(enigma->rotors);
        free(enigma);
        return NULL;
    }

    for (size_t i = 0; i < num_rotors; i++) {
        enigma->rotors[i] = rotors[i];
        enigma->rings[i] = rings[i];
        enigma->inits[i] = inits[i];
    }

    enigma->reflector = reflector;

    enigma->num_pairs = num_pairs;
    enigma->pairs = pairs;

    return enigma;
}

char *encrypt_Enigma(Enigma *self, char *dst, const char *src)
{
    size_t num_rotors = self->num_rotors;
    const char **rotors = self->rotors;
    size_t *rings = self->rings;
    size_t *inits = self->inits;
    const char *reflector = self->reflector;
    const char *pairs = self->pairs;

    char *result = malloc(strlen(src) + 1);
    result[0] = '\0';

    const char *current = src;

    struct plugboard Plugboard;
    initPlugboard(&Plugboard);
    switchPairs(&Plugboard, pairs);

    struct reflector Reflector;
    initReflector(&Reflector, reflector);

    struct Rotor rotor[num_rotors];
    for (size_t i = 0; i < num_rotors; i++) {
        initRotor(&rotor[i], rotors[i], rings[i], inits[i]);
        rotateLetter(&rotor[i], rotors[i][inits[i]]);
        setRing(&rotor[i], rings[i]);
    }

    while (*current != '\0') {
        if (*current == ' ') {
            strcat(result, current);
        } else {
            tick_Enigma(self);
            int input = *current - 'A';
            processInput(&Plugboard, input);
            for (size_t i = 0; i < num_rotors; i++) {
                input = forward(&rotor[i], input);
            }
            reflecting(&Reflector, input);
            for (size_t i = num_rotors; i > 0; i--) {
                size_t index = i - 1;
                input = backward(&rotor[index], input);
            }
            processInput(&Plugboard, input);
            input = input + 'A';
            char output = (char)input;
            strcat(result, &output);
        }
        current++;
    }
    strcpy(dst, result);
    free(result);
    return dst;
}

void tick_Enigma(Enigma *self)
{
    size_t num_rotors = self->num_rotors;
    const char **rotors = self->rotors;

    for (size_t i = 0; i < num_rotors; i++) {
        struct Rotor rotor;
        initRotor(&rotor, rotors[i], self->rings[i], self->inits[i]);
        if (rotor.left[0] == rotor.turnover) {
            rotate(&rotor, 1, true);
            self->inits[i] = (self->inits[i] + 1) % 26;
        }
    }
}

void reset_rotor_Enigma(Enigma *self, size_t *new_setting)
{
    size_t num_rotors = self->num_rotors;

    for (size_t i = 0; i < num_rotors; i++) {
        self->inits[i] = new_setting[i] % 26;
    }
}

#define MAX_SIZE 26

void free_Enigma(struct Enigma* self) {
    for (size_t i = 0; i < self->num_rotors; i++) {
        free((void*)self->rotors[i]);
    }
    free(self->rotors);
    free(self->rings);
    free(self->inits);
    free((void*)self->reflector);
    free((void*)self->pairs);
    free(self);
}

void get_setting_Enigma(struct Enigma* self, char* ret) {
    for (size_t i = 0; i < self->num_rotors; i++) {
        const char* rotor = self->rotors[i];
        ret[i] = rotor[self->inits[i]];
    }
    ret[self->num_rotors] = '\0';
}

void tick_n_Enigma(struct Enigma* self, size_t n) {
    for (size_t i = 0; i < n; i++) {
        tick_Enigma(self);
    }
}

