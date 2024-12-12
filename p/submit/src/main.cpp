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
  typedef std::unordered_multimap< Q_t_S_t, Q_t > MD_t;
  
  S_t a = "a";
  S_t b = "b";
  S_t e = "epsilon";

  Q_t q0 = "q0";
  Q_t q1 = "q1";
  Q_t q2 = "q2";
  Q_t q3 = "q3";
  Q_t q4 = "q4";
  Q_t q5 = "q5";
  
  //=========================================================
  //Standard Sigma initilization
  //=========================================================
  std::unordered_set< S_t > S {a, b};

  //=========================================================
  //Nfa0 initilization
  //=========================================================
  std::unordered_set< Q_t > Q0 {q0};
  std::unordered_set< Q_t > F0 {q0};

  MD_t delta0;
  delta0.insert({{q0, a}, q0});
  
  NFA< S_t, Q_t > Nfa0(S, Q0, q0, F0, delta0);
  
  //=========================================================
  //Nfa1 initilization
  //=========================================================
  std::unordered_set< Q_t > Q1 {q0, q1, q2};
  std::unordered_set< Q_t > F1 {q2};

  MD_t delta1;
  delta1.insert({{q0, b}, q1});

  delta1.insert({{q1, a}, q2});
  delta1.insert({{q1, b}, q1});

  NFA< S_t, Q_t > Nfa1(S, Q1, q0, F1, delta1);

  //=========================================================
  //Dfa initilization
  //=========================================================
  std::unordered_set< S_t > Q {q0, q1}; // Q
  std::unordered_set< S_t > F {q1}; // F
  
  D_t delta; //delta
  delta[{q0, a}] = q0;
  delta[{q0, b}] = q1;
  delta[{q1, a}] = q1;
  delta[{q1, b}] = q0;

  DFA< S_t, Q_t > M(S, Q, q0, F, delta);


  NFA< S_t, Q_t > Nfa2(M);

  std::list< S_t > w0 {a, a, a};
  std::list< S_t > w1 {b, b, a};
  std::cout << Nfa0 << std::endl;
  std::cout << Nfa0(w0) << '\n'; // M(w) is true if M accepts abaa
  std::cout << Nfa0(w1) << '\n'; // M(w) is true if M accepts abaa
  
  std::cout << Nfa1 << std::endl;
  std::cout << Nfa1(w0) << '\n'; // M(w) is true if M accepts abaa
  std::cout << Nfa1(w1) << '\n'; // M(w) is true if M accepts abaa
  
  std::cout << Nfa2 << std::endl;
  std::cout << Nfa2(w0) << '\n'; // M(w) is true if M accepts abaa
  std::cout << Nfa2(w1) << '\n'; // M(w) is true if M accepts abaa
  
  return 0;
}
