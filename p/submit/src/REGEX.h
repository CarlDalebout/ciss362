#ifndef REGEX_H
#define REGEX_H

#include <iostream>
#include <string>
#include "STL_util.h"
#include "NFA.h"

// Forward declare NFA
template <typename S, typename T>
class NFA;

class REGEX
{
  public: 
    REGEX()
    {std::cout << "called default constructor" << std::endl;}

    REGEX(const std::string & experession)
    :expression_(experession)
    {}

    // template < typename S, typename T>
    // REGEX(const NFA<S, T> & x)
    // {
    //   std::cout << "incomplete\n";
    // }
    
    template <typename S>
    bool operator()(const std::vector<S>& word) const
    {
      for (const auto& symbol : word)
      {
        
      }
    }

    template <typename S>
    bool operator()(const std::list<S>& word) const 
    {

    }

  private:
    std::string expression_;
};
#endif    