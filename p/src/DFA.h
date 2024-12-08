#ifndef DFA_H
#define DFA_H

#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include "STL_util.h"

template < typename S, typename T>
class DFA
{
  public:
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

    // Getter functions
    const std::unordered_set<S>& alpha() const { return alphabet_; }
    const std::unordered_set<T>& getStates() const { return states_; }
    const T& getStartState() const { return start_state_; }
    const std::unordered_set<T>& getAcceptingStates() const { return accepting_states_; }
    const std::unordered_map<std::pair<T, S>, T> & getTransitionFunction() const { return delta_; }

    // Setter functions
    void alpha(const std::unordered_set<S>& alphabet) { alphabet_ = alphabet; }
    void setStates(const std::unordered_set<T>& states) { states_ = states; }
    void setStartState(const T& start_state) { start_state_ = start_state; }
    void setAcceptingStates(const std::unordered_set<T>& accepting_states) { accepting_states_ = accepting_states; }
    void setTransitionFunction(const std::unordered_map<std::pair<T, S>, T> & delta) { delta_ = delta; }

    bool operator()(const std::vector<S>& word) const 
    {
      T current_state = start_state_;  // Start at the initial state

        // Process each symbol in the word
        for (const auto& symbol : word) {
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
  
  private:
    std::unordered_set<S>                   alphabet_;          // Set of input symbols
    std::unordered_set<T>                   states_;            // Set of states
    T                                       start_state_;       // Initial state
    std::unordered_set<T>                   accepting_states_;  // Set of accepting states
    std::unordered_map<std::pair<T, S>, T>  delta_;             // Map of transitions
};

#endif