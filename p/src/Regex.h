#ifndef REGEX_H
#define REGEX_H

#include <iostream>
#include <string>
#include "NFA.h"
#include "STL_util.h"

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