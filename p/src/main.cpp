#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include "STL_util.h"
#include "DFA.h"
#include "NFA.h"

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
  std::unordered_set< Q_t > Q0 {q0, q1, q2};
  std::unordered_set< Q_t > Q1 {q0, q1};
  std::unordered_set< Q_t > F0 {q1, q2};
  std::unordered_set< Q_t > F1 {q1};

  D_t delta0;
  delta0[{q0, a}] = q1;
  delta0[{q0, b}] = q0;
  
  delta0[{q1, a}] = q1;
  delta0[{q1, b}] = q2;
  
  delta0[{q2, a}] = q2;
  delta0[{q2, b}] = q2;

  
  
  D_t delta1;
  delta1[{q0, a}] = q0;
  delta1[{q0, b}] = q1;
  
  delta1[{q1, a}] = q1;
  delta1[{q1, b}] = q1;


  DFA< S_t, Q_t >   M0(S, Q0, q0, F0, delta0);
  DFA< S_t, Q_t >   M1(S, Q1, q0, F1, delta1);
  DFA< S_t, Q_t>    M2(M0.intersection(M1));

  NFA< S_t, Q_t > nfaM(S, Q0, q0, F0, delta0);

  std::list< S_t > w {a, b, a, a};
  std::cout << M0(w) << '\n'; // M(w) is true if M accepts abaa
  std::cout << M0.complement(w) << '\n';
  
  std::cout << nfaM(w) << '\n'; // M(w) is true if M accepts abaa
  return 0;
}