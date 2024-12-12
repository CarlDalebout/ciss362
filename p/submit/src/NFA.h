#ifndef NFA_H
#define NFA_H

#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <bits/stdc++.h>
#include "STL_util.h"
#include "DFA.h"
#include "REGEX.h"

// Forward declare DFA
template <typename S, typename T>
class DFA;

// Forward declare REGEX
class REGEX;

template < typename S, typename T>
class NFA
{
  public:
    // Default constructor
    NFA()
      : alphabet_({}), 
        states_({}), 
        start_state_(""), 
        accepting_states_({}),
        delta_({})
      {}
    
    // Standard constructor
    NFA(const std::unordered_set<S> & s, 
        const std::unordered_set<T> & q, 
        T & q0, 
        const std::unordered_set<T> & f, 
        const std::unordered_multimap<std::pair<T, S>, T> delta)
    : alphabet_(s), 
      states_(q), 
      start_state_(q0), 
      accepting_states_(f),
      delta_(delta)
    {}

    // copy constructor
    NFA(const NFA<S, T> & x)
    {
      alphabet_         = x.alpha(); 
      states_           = x.states();
      start_state_      = x.start_state();
      accepting_states_ = x.accepting_states();
      delta_ = x.delta();
    }
      
    // DFA to NFA constructor
    NFA(const DFA<S, T> & x)
    {
      alphabet_ = x.alpha();
      states_ = x.states();
      start_state_ = x.start_state();
      accepting_states_ = x.accepting_states();
      std::unordered_multimap<std::pair<T, S>, T> temp;
      for(auto& itr : x.delta())
      {
        temp.insert({itr.first, itr.second});
      }
      delta_ = temp;
    }

    //-----------------------------------------------------------------------------
    //  Getter Functions
    //-----------------------------------------------------------------------------
    const std::unordered_set<S>& alpha() const { return alphabet_; }
    const std::unordered_set<T>& states() const { return states_; }
    const T& start_state() const { return start_state_; }
    const std::unordered_set<T>& accepting_states() const { return accepting_states_; }
    const std::unordered_multimap<std::pair<T, S>, T> & delta() const { return delta_; }

    //-----------------------------------------------------------------------------
    // Setter Functions
    //-----------------------------------------------------------------------------
    void alpha(const std::unordered_set<S>& alphabet) { alphabet_ = alphabet; }
    void states(const std::unordered_set<T>& states) { states_ = states; }
    void start_state(const T& start_state) { start_state_ = start_state; }
    void accepting_states(const std::unordered_set<T>& accepting_states) { accepting_states_ = accepting_states; }
    void delta(const std::unordered_multimap<std::pair<T, S>, T> & delta) { delta_ = delta; }

    bool operator()(const std::vector<S>& word) const 
    {
      std::unordered_set< T > current_states = {start_state_};  // Start at the initial state
      
      // Process each symbol in the word
      for(const auto& symbol : word)
      {
        std::unordered_set<T> new_states;

        // testing each state in current_states
        for (auto& itr : current_states)
        {
          std::unordered_multimap<std::pair<T, S>, T> temp_delta = delta_;
          auto transition = temp_delta.find({itr, symbol});
          if (transition != temp_delta.end()) 
          {
            while(transition != temp_delta.end())
            {
              new_states.insert(transition->second);
              temp_delta.erase(transition);
              transition = temp_delta.find({itr, symbol});
            }
          }
          
          //check epsilon
          transition = temp_delta.find({itr, "epsilon"});
          if (transition != temp_delta.end()) 
          {
            while(transition != temp_delta.end())
            {
              new_states.insert(transition->second);
              temp_delta.erase(transition);
              transition = temp_delta.find({itr, "epsilon"});
            }
          }
        }
        
        // std::cout << new_states << std::endl;
        current_states = new_states;
      }

      // The word is accepted if the final state is in the accepting_states
      for(auto& it : current_states)
      {
        if(accepting_states_.find(it) != accepting_states_.end())
          return true;
      }

      return false;
    }

    bool operator()(const std::list<S>& word) const 
    {
      std::list<S> temp = word;
      std::unordered_set< T > current_states = {start_state_};  // Start at the initial state
      
      // Process each symbol in the word
      while(temp.size() > 0)
      {
        // get symbol from the stack
        S symbol = temp.front();
        temp.pop_front();
        std::unordered_set<T> new_states;

        // testing each state in current_states
        for (auto& itr : current_states)
        {
          std::unordered_multimap<std::pair<T, S>, T> temp_delta = delta_;
          auto transition = temp_delta.find({itr, symbol});
          if (transition != temp_delta.end()) 
          {
            while(transition != temp_delta.end())
            {
              new_states.insert(transition->second);
              temp_delta.erase(transition);
              transition = temp_delta.find({itr, symbol});
            }
          }
          
          //check epsilon
          transition = temp_delta.find({itr, "epsilon"});
          if (transition != temp_delta.end()) 
          {
            while(transition != temp_delta.end())
            {
              new_states.insert(transition->second);
              temp_delta.erase(transition);
              transition = temp_delta.find({itr, "epsilon"});
            }
          }
        }
        
        // std::cout << new_states << std::endl;
        current_states = new_states;
      }

      // The word is accepted if the final state is in the accepting_states
      for(auto& it : current_states)
      {
        if(accepting_states_.find(it) != accepting_states_.end())
          return true;
      }

      return false;
    }

    // std::vector<std::pair<T, std::vector<S>>> IDs(const std::vector<S>& word) const
    // {
    //   std::vector<std::pair<T, std::vector<S>>> ret;
    //   std::vector<S> temp = word;
    //   T current_state = start_state_;  // Start at the initial state
    //   std::cout << temp << std::endl;  // Print out the current word
    //
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

    //This assumes that both NFA's has the same S
    NFA<S, T> getUnion(const NFA<S, T> x)
    {
      //getting newS
      std::unordered_set< S > newS = alphabet_;
      
      //getting newstart
      T newInit = "ql";

      //getting newQ
      std::unordered_set< T > newQ = {"ql"};
      for(auto& itr : states_)
      {
        newQ.insert("0" + itr);
      }
      for(auto& itr : x.states())
      {
        newQ.insert("1" + itr);
      }
      
      //getting newF
      std::unordered_set< T > newF;
      for(auto& itr : accepting_states_)
      {
        newF.insert("0" + itr);
      }
      for(auto& itr : x.accepting_states())
      {
        newF.insert("1" + itr);
      }

      //getting newDelta
      std::unordered_multimap<std::pair<T, S>, T>  newDelta = {{{"ql", "epsilon"}, ("0" + start_state_)},
                                                               {{"ql", "epsilon"}, ("1" + x.start_state())}};
      for(auto& itr : delta_)
      {
        newDelta.insert({{"0" + itr.first.first, itr.first.second}, ("0" + itr.second)});
      }
      for(auto& itr : x.delta())
      {
        newDelta.insert({{"1" + itr.first.first, itr.first.second}, ("1" + itr.second)});
      }


      NFA< S, T > ret(newS, newQ, newInit, newF, newDelta);
      return ret;
    }

    //This assumes that both NFA's has the same S
    NFA<S, T> concatenation(const NFA<S, T> x)
    {
      //getting newS
      std::unordered_set< S > newS = alphabet_;
      
      //getting newstart
      T newInit = ("0" + start_state_);

      //getting newQ
      std::unordered_set< T > newQ;
      for(auto& itr : states_)
      {
        newQ.insert("0" + itr);
      }
      for(auto& itr : x.states())
      {
        newQ.insert("1" + itr);
      }
      
      //getting newF
      std::unordered_set< T > newF;
      for(auto& itr : x.accepting_states())
      {
        newF.insert("1" + itr);
      }

      //getting newDelta
      std::unordered_multimap<std::pair<T, S>, T>  newDelta;
      for(auto& itr : delta_)
      {
        newDelta.insert({{"0" + itr.first.first, itr.first.second}, ("0" + itr.second)});
      }
      for(auto& itr : x.delta())
      {
        newDelta.insert({{"1" + itr.first.first, itr.first.second}, ("1" + itr.second)});
      }
      for(auto& itr : accepting_states_)
      {
        newDelta.insert({{"0" + itr.first.first, "epsilon"}, ("1" + x.start_state())});
      }


      NFA< S, T > ret(newS, newQ, newInit, newF, newDelta);
      return ret;
    }

    NFA<S, T> KleenStar()
    {
      //getting newS
      std::unordered_set< S > newS = alphabet_;
      
      //getting newstart
      T newInit = ("qs");

      //getting newQ
      std::unordered_set< T > newQ = states_;
      newQ.insert("qs");
      
      //getting newF
      std::unordered_set< T > newF = accepting_states_;
      newF.insert("qs");

      //getting newDelta
      std::unordered_multimap<std::pair<T, S>, T>  newDelta = delta_;
      for(auto& itr : accepting_states_)
      {
        newDelta.insert({{itr.first.first, "epsilon"}, start_state_});
      }


      NFA< S, T > ret(newS, newQ, newInit, newF, newDelta);
      return ret;
    }

  private:
    std::unordered_set<S>                       alphabet_;         // Set of input symbols
    std::unordered_set<T>                       states_;           // Set of states
    T                                           start_state_;      // Initial state
    std::unordered_set<T>                       accepting_states_; // Set of accepting states
    std::unordered_multimap<std::pair<T, S>, T> delta_;            // Map of transitions
};

template < typename S, typename T >
std::ostream & operator<<(std::ostream & cout, const NFA<S, T> & x)
{
  cout << "alpha: "            << x.alpha()            << std::endl;
  cout << "states: "           << x.states()           << std::endl;
  cout << "start_state: "      << x.start_state()      << std::endl;
  cout << "accepting_states: " << x.accepting_states() << std::endl;
  cout << "delta: "            << x.delta()            << std::endl;
  return cout;
}

#endif