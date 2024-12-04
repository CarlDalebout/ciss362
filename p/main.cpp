#include <iostream>
#include <string>
#include <vector>
#include <utility>
#include <unordered_set>
#include <unordered_map>

namespace std
{
  std::string to_string(char c)
  {
    return {c};
  }

  std::string to_string(const std::string & x)
  {
    return x;
  }

  template < typename S, typename T>
  std::string to_string(const std::pair< S, T> & x)
  {
    return std::string("Incomplete")
  }

  template < typename T>
  std::string to_string(const std::vector<T> & x)
  {
    return std::string("Incomplete")
  }

  template < typename T>
  std::string to_string(const std::unordered_set<T> & x)
  {
    return std::string("Incompleted")
  }
  
  // template < typename T>
  // std::string to_string(const std::unordered_map<T> & x)
  // {
  //   return std::string("Incompleted")
  // }
}


int main()
{
  // std::cout << "Testing std::to_string\n";
  // std::cout << "int: " << std::to_string(42) << '\n';
  // std::cout << "double: " << std::to_string(3.14) << '\n';
  std::cout << "Testing std::to_string\n";
  std::cout << "int: " << std::to_string(42) << '\n';
  std::cout << "double: " << std::to_string(3.14) << '\n';
  std::cout << "char: " << std::to_string('a') << '\n';
  std::cout << "bool: " << std::to_string(true) << '\n';
  std::cout << "unsigned int: " << std::to_string((unsigned int)(-1)) << '\n';
  std::cout << "std::string: "  << std::to_string("hello world") << '\n';
  std::cout << "std::pair< int, int >: "
            << std::to_string(std::make_pair(42, 43)) << '\n';
  std::cout << "std::pair< int, double >: "
            << std::to_string(std::make_pair(42, 3.14)) << '\n';
  std::cout << "std::pair< int, char >: "
            << std::to_string(std::make_pair(42, 'a')) << '\n';
  std::cout << "std::pair< int, bool >: "
            << std::to_string(std::make_pair(42, true)) << '\n';
  std::cout << "std::pair< int, unsigned int>: "
            << std::to_string(std::make_pair(-1, (unsigned int)(-1))) << '\n';
  std::cout << "std::pair< std::pair< int, int > int >: "
            << std::to_string(std::make_pair(std::make_pair(42, 43), 44)) << '\n';
  std::cout << "std::pair< int, std::pair< int, int > >: "
            << std::to_string(std::make_pair(42, std::make_pair(43, 44))) << '\n';
  std::cout << "std::vector< int >: "
            << std::to_string(std::vector< int >{2, 3, 5}) << '\n';
  std::cout << "std::vector< double >: "
            << std::to_string(std::vector< double >{1.2, 3.4, 5.6}) << '\n';
  std::cout << "std::vector< char >: "
            << std::to_string(std::vector< char >{'a', 'b', 'c'}) << '\n';
  std::cout << "std::vector< std::string >: "
            << std::to_string(std::vector< std::string >{"ab", "cd", "ef"}) << '\n';
  std::cout << "std::pair< int, int >: "
            << std::to_string(std::pair< int, int >{42, 43}) << '\n';
  std::cout << "std::unordered_map< int, int >: "
            << std::to_string(std::unordered_map< int, int>{{42,1}, {43,2}, {44,3}}) << '\n';
  std::cout << "std::unordered_map< std::pair< int, int >, int>: "
            << std::to_string(std::unordered_map< std::pair< int, int>, int >{{{42,1},2}, {{43,2},3}, {{44,3},4} }) << '\n';
}