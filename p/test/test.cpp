#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include "../src/STL_util.h"



int main()
{
  typedef std::string Q_t;
  typedef std::string S_t;
  typedef std::pair< Q_t, S_t > Q_t_S_t;
  typedef std::unordered_map< Q_t_S_t, Q_t > D_t;
  typedef std::unordered_multimap< Q_t_S_t , Q_t> MD_t;
 
  S_t a = "a";
  S_t b = "b";
  S_t e = "epsilon";

  Q_t q0 = "q0";
  Q_t q1 = "q1";
  Q_t q2 = "q2";
  Q_t q3 = "q3";
  Q_t q4 = "q4";
  Q_t q5 = "q5";
  
  std::unordered_set< S_t > S {a, b};

  std::unordered_set< Q_t > Q {q0, q1, q2};

  std::unordered_set< Q_t > current_states = {q0, q1};  // Start at the initial state

  std::unordered_set< Q_t > F {q2};

  MD_t delta;
  delta.insert({{q0, a}, q0});
  delta.insert({{q0, b}, q0});
  delta.insert({{q0, b}, q1});

  delta.insert({{q1, a}, q0});
  delta.insert({{q1, b}, q1});

  delta.insert({{q2, a}, q2});
  delta.insert({{q2, b}, q2});

  for(auto& x : delta)
  {
    std::cout << x << std::endl;
  }

  return 0;
}