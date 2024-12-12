#ifndef DFA_H
#define DFA_H

#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include "NFA.h"
#include "STL_util.h"

// Forward declare NFA
template <typename S, typename T>
class NFA;

template < typename S, typename T>
class DFA
{
  public:
    DFA()
    : alphabet_({}), 
      states_({}), 
      start_state_(""), 
      accepting_states_({}),
      delta_({})
    {}

    DFA(const std::unordered_set<S> & s, 
        const std::unordered_set<T> & q, 
        T & q0, 
        const std::unordered_set<T> & f, 
        const std::unordered_map<std::pair<T, S>, T> delta)
    : alphabet_(s), 
      states_(q), 
      start_state_(q0), 
      accepting_states_(f),
      delta_(delta)
    {}

    DFA(const DFA<S, T> & x)
    {
      alphabet_         = x.alpha(); 
      states_           = x.states();
      start_state_      = x.start_state();
      accepting_states_ = x.accepting_states();
      delta_            = x.delta();
    }
 
    DFA(const NFA<S, T> & x)
    {
      std::cout << "incomplete\n";
    }

    //-----------------------------------------------------------------------------
    //  Getter Functions
    //-----------------------------------------------------------------------------
    const std::unordered_set<S>& alpha() const { return alphabet_; }
    const std::unordered_set<T>& states() const { return states_; }
    const T& start_state() const { return start_state_; }
    const std::unordered_set<T>& accepting_states() const { return accepting_states_; }
    const std::unordered_map<std::pair<T, S>, T> & delta() const { return delta_; }

    //-----------------------------------------------------------------------------
    // Setter Functions
    //-----------------------------------------------------------------------------
    void alpha(const std::unordered_set<S>& alphabet) { alphabet_ = alphabet; }
    void states(const std::unordered_set<T>& states) { states_ = states; }
    void start_state(const T& start_state) { start_state_ = start_state; }
    void accepting_states(const std::unordered_set<T>& accepting_states) { accepting_states_ = accepting_states; }
    void delta(const std::unordered_map<std::pair<T, S>, T> & delta) { delta_ = delta; }

    bool operator()(const std::vector<S>& word) const 
    {
      T current_state = start_state_;  // Start at the initial state

        // Process each symbol in the word
        for (const auto& symbol : word) 
        {
          // Find the next state based on current state and input symbol
          auto transition = delta_.find({current_state, symbol});
          if (transition == delta_.end()) {
              return false;  // No transition found, the word is rejected
          }
          current_state = transition->second;  // Move to the next state
        }

        // The word is accepted if the final state is in the accepting states
        return accepting_states_.count(current_state) > 0;
    }

    bool operator()(const std::list<S>& word) const 
    {
      std::list<S> temp = word;
      T current_state = start_state_;  // Start at the initial state
      
      // Process each symbol in the word
      while(temp.size() > 0)
      {
        S symbol = temp.front();
        temp.pop_front();

        // Find the next state based on current state and input symbol
        auto transition = delta_.find({current_state, symbol});
        if (transition == delta_.end()) {
            return false;  // No transition found, the word is rejected
        }
        current_state = transition->second;  // Move to the next state
      }

      // The word is accepted if the final state is in the accepting states
      return accepting_states_.count(current_state) > 0;
    }
    
    // std::vector<std::pair<T, std::vector<S>>> IDs(const std::vector<S>& word) const
    // {
    //   std::vector<std::pair<T, std::vector<S>>> ret;
    //   std::vector<S> temp = word;
    //   T current_state = start_state_;  // Start at the initial state
    //   std::cout << temp << std::endl;  // Print out the current word
    //     // Process each symbol in the word
    //     while(temp.size() > 0) 
    //     {
    //       S symbol = temp[0];
    //       // Find the next state based on current state and input symbol
    //       auto transition = delta_.find({current_state, symbol});
    //       if (transition == delta_.end()) {
    //           return false;  // No transition found, the word is rejected
    //       }
    //       current_state = transition->second;  // Move to the next state
    //     }
    //
    //     // The word is accepted if the final state is in the accepting states
    //     return accepting_states_.count(current_state) > 0;
    // }

    bool complement(const std::list<S>& word) const
    {
      std::list<S> temp = word;
      T current_state = start_state_;  // Start at the initial state
      // std::cout << temp << std::endl;
      
      // Process each symbol in the word
      while(temp.size() > 0)
      {
        // std::cout << std::pair<T, std::list<S>>{current_state, temp} << std::endl;
        S symbol = temp.front();
        temp.pop_front();
        // Find the next state based on current state and input symbol
        auto transition = delta_.find({current_state, symbol});
        if (transition == delta_.end()) {
            return false;  // No transition found, the word is rejected
        }
        current_state = transition->second;  // Move to the next state
      }

      // The word is accepted if the final state is in the accepting states
      // std::cout << std::pair<T, std::list<S>>{current_state, temp} << std::endl;
      return accepting_states_.count(current_state) <= 0;
    }

    DFA<S, T> intersection(const DFA<S, T> x) //This assumes that both DFA's has the same S
    {
      //getting newS
      std::unordered_set< S > newS = alphabet_;
      
      //getting newQ
      std::unordered_set< T > newQ;
      for(auto& it : states_)
        for(auto& jt : x.states())
        {
          newQ.insert(it+jt);
        }
      
      //getting newstart
      T newInit = start_state_+x.start_state();

      //getting newF
      std::unordered_set< T > newF;
      std::unordered_set< T > xaccepting_states = x.accepting_states();
      for(auto& it : states_)
        for(auto& jt : x.states())
        {

          if((accepting_states_.find(it) != accepting_states_.end()) || (xaccepting_states.find(jt) != xaccepting_states.end()))
            newF.insert(it+jt);
        }

      //getting newDelta
      std::unordered_map<std::pair<T, S>, T>  xdelta_ = x.delta();
      std::unordered_map<std::pair<T, S>, T>  newDelta;

      for(auto& symbol : alphabet_)
        for(auto& it : states_)
          for(auto& jt : x.states())
          {
            auto tran0 = delta_.find({it, symbol});
            auto tran1 = xdelta_.find({jt, symbol});
            newDelta[{(tran0->first.first + tran1->first.first), symbol}] = (tran0->second + tran1->second);
          }

      DFA<S, T> ret(newS, newQ, newInit, newF, newDelta);
      return ret;
    }

  private:
    std::unordered_set<S>                   alphabet_;          // Set of input symbols
    std::unordered_set<T>                   states_;            // Set of states
    T                                       start_state_;       // Initial state
    std::unordered_set<T>                   accepting_states_;  // Set of accepting states
    std::unordered_map<std::pair<T, S>, T>  delta_;             // Map of transitions
};

template < typename S, typename T >
std::ostream & operator<<(std::ostream & cout, const DFA<S, T> & x)
{
  cout << "alpha: "            << x.alpha()            << std::endl;
  cout << "states: "           << x.states()           << std::endl;
  cout << "start_state: "      << x.start_state()      << std::endl;
  cout << "accepting_states: " << x.accepting_states() << std::endl;
  cout << "delta: "            << x.delta()            << std::endl;
  return cout;
}

#endif