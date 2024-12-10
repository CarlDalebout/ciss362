#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include "src/STL_util.h"
#include "src/DFA.h"
#include "src/NFA.h"

int main()
{
  typedef std::string Q_t;
  typedef std::string S_t;
  typedef std::pair< Q_t, S_t > Q_t_S_t;
  typedef std::unordered_map< Q_t_S_t, Q_t > D_t;
  
  S_t a = "a";
  S_t b = "b";
  Q_t q0 = "q0";
  Q_t q1 = "q1";
  Q_t q2 = "q2";
  
  std::unordered_set< S_t > S {a, b};
  std::unordered_set< Q_t > Q {q0, q1, q2};
  std::unordered_set< Q_t > F {q1};

  D_t delta;
  delta[{q0, a}] = q0;
  delta[{q0, b}] = q1;
  delta[{q1, a}] = q1;
  delta[{q1, b}] = q2;
  delta[{q2, a}] = q0;
  delta[{q2, b}] = q2;

  DFA< S_t, Q_t > M(S, Q, q0, F, delta);
  NFA< S_t, Q_t > nfaM(M);

  std::list< S_t > w {a, b, a, a};
  std::cout << M(w) << '\n'; // M(w) is true if M accepts abaa
  return 0;
}