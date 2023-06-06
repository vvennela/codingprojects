#ifndef ENIGMA_IMPL_H
#define ENIGMA_IMPL_H

#include "Enigma.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


struct Enigma {
  size_t num_rotors;
  const char** rotors;
  size_t* rings;
  size_t* inits;
  const char* reflector;
  size_t num_pairs;
  const char* pairs;
};

#endif
