#ifndef STL_UTIL_H
#define STL_UTIL_H

#include <iostream>
#include <vector>
#include <string>
#include <list>
#include <unordered_set>
#include <unordered_map>
#include <set>
#include <algorithm>

//=============================================================================
// Prototypes
//
// * std::string to_string(T) where T = int(Done), double(Done) char(Done), bool(Done),
//                                      const std::string &                 (Done),
//                                      const std::pair< X, Y > &           (Done),
//                                      const std::vector< X > &            (Done),
//                                      const std::list< X > & ... TODO     (Done),
//                                      const std::unordered_map< X, Y > &  (Done),
//                                      const std::unordered_set< X > &     (Done)
//
// * std::hash< T > where T = int(Done), double(Done), char(Done), bool(Done),
//                            const std::string &                      (Done),
//                            const std::pair< X, Y > &                (Done),
//                            const std::vector< X > &                 (Done),
//                            const std::list< X > &                   (Done),
//                            const std::unordered_map< X, Y > &       (Done),
//                            const std::unordered_set< X > &          (Done)
//
//-----------------------------------------------------------------------------
// * set membership (Done)
//-----------------------------------------------------------------------------
// If C is a container and e is an element, use one of the following for
// membership check:
// has< T, S > (C, e)
// is_member< S, T >(e, C) where T is a container of S-values and
// T::find(const S &) is defined
// 
//-----------------------------------------------------------------------------
// * set difference
//-----------------------------------------------------------------------------
// If X, Y, Z are containers of type std::set< T >, std::unordered_set< T >
// X -= Y
// Z = X - Y
// (See also C++ std::set_difference)
//
//-----------------------------------------------------------------------------
// * set union
//-----------------------------------------------------------------------------
// If X, Y, Z are containers of type std::set< T >, std::unordered_set< T >
// X |= Y // X = X union with Y
// Z = X | Y // Z = X union with Y
// (See also std::set_union)
//
//-----------------------------------------------------------------------------
// * set intersection
//-----------------------------------------------------------------------------
// If X, Y, Z are containers of type std::set< T >, std::unordered_set< T >
// X &= Y
// Z = X & Y
// (See also C++ std::set_intersection)
//
//-----------------------------------------------------------------------------
// * cross product
//-----------------------------------------------------------------------------
// If X, Y, Z are containers of type std::set< T >, std::unordered_set< T >
// Z = crossprod(X, Y)
//
//-----------------------------------------------------------------------------
// * powerset
//-----------------------------------------------------------------------------
// If X, Z are containers of type of std::set< T >, std::unordered_set< T >
// Z = powset(X)
//
//=============================================================================

//-----------------------------------------------------------------------------
// Prototypes of std::to_string extensions
//-----------------------------------------------------------------------------
namespace std
{
  inline
  std::string to_string(char c);

  inline
  std::string to_string(const std::string & x);

  template < typename S, typename T >
  std::string to_string(const std::pair< S, T > & x);

  // template < typename T >
  // std::string container_to_string_(const T & x, 
  //                                  const std::string & begin, 
  //                                  const std::string & end);
  
  template < typename T >
  std::string to_string(const std::vector< T > & x);
  
  template < typename T >
  std::string to_string(const std::list< T > & x);
  
  template < typename T >
  std::string to_string(const std::unordered_set< T > & x);
  
  // template < typename S, typename T, typename LESS >
  // std::string to_string(const std::unordered_map< S, T > & x,
  //                       const LESS & less);
  
  template < typename S, typename T >
  std::string to_string(const std::unordered_map< S, T > & x);
  
  // template < typename T, typename LESS >
  // std::string to_string(const std::unordered_set< T > & x,
  //                       const LESS & less);
  
  template <typename T >
  std::string to_string(const std::set< T > & x);
  
  // template < typename T, typename LESS >
  // std::string to_string(const std::set< T > & x, const LESS & less);
};

//-----------------------------------------------------------------------------
// Prototypes of std::hash extensions
//-----------------------------------------------------------------------------
namespace std
{
  template < typename S, typename T >
  struct hash< std::pair< S, T > >;
  
  template < typename T >
  struct hash< std::vector< T > >;
  
  template < typename T >
  struct hash< std::list< T > >;
  
  template < typename T >
  struct hash< std::unordered_set< T > >;
  
  // template < typename S, typename T, typename H >
  // struct hash< std::unordered_map< S, T, H > >;
  
  template < typename S >
  struct hash< std::set< S > >;
}

//-----------------------------------------------------------------------------
// Prototypes of membership
//-----------------------------------------------------------------------------
template < typename S, typename T >
bool is_member(const S & e, const T & X);

template < typename S, typename T >
bool has(const S & X, const T & e);

//-----------------------------------------------------------------------------
// Prototypes for set difference
//-----------------------------------------------------------------------------
template < typename T0, typename T1 >
void set_difference_(T0 & X, const T1 & Y);

template < typename T >
const std::unordered_set< T > & operator-=(std::unordered_set< T > & X,
                                           const std::unordered_set< T > & Y);

template < typename T >
std::unordered_set< T > operator-(const std::unordered_set< T > & X,
                                  const std::unordered_set< T > & Y);

template < typename T >
const std::set< T > & operator-=(std::set< T > & X, const std::set< T > & Y);

template < typename T >
std::set< T > operator-(const std::set< T > & X, const std::set< T > & Y);

//-----------------------------------------------------------------------------
// Prototypes of set union
//-----------------------------------------------------------------------------
template < typename T >
void set_union(T & x, const T & y);

template < typename T >
std::set< T > & operator|=(std::set< T > & x, const std::set< T > & y);

template < typename T >
std::set< T > operator|(const std::set< T > & x, const std::set< T > & y);

template < typename T >
std::unordered_set< T > & operator|=(std::unordered_set< T > & x,
                                     const std::unordered_set< T > & y);

template < typename T >
std::unordered_set< T > operator|(const std::unordered_set< T > & x,
                                  const std::unordered_set< T > & y);

//-----------------------------------------------------------------------------
// Prototypes of set intersection
//-----------------------------------------------------------------------------
template < typename T >
void set_intersection_(T & xs, const T & ys);

template < typename T >
std::set< T > & operator&=(std::set< T > & xs, const std::set< T > & ys);

template < typename T >
std::set< T > operator&(std::set< T > & x, const std::set< T > & y);

template < typename T >
std::unordered_set< T > operator&=(std::unordered_set< T > & xs,
                                   const std::unordered_set< T > & ys);

template < typename T >
std::unordered_set< T > operator&(std::unordered_set< T > & x,
                                  const std::unordered_set< T > & y);

//-----------------------------------------------------------------------------
// Prototypes of cross product
//-----------------------------------------------------------------------------
template < typename T0, typename T1, typename T2 >
void crossprod_(T0 & ret, const T1 & xs, const T2 & ys);

template < typename T0, typename T1 >
std::set< std::pair< T0, T1 > > crossprod(const std::set< T0 > & xs,
                                          const std::set< T1 > & ys);

template < typename T0, typename T1 >
std::unordered_set< std::pair< T0, T1 > > crossprod(const std::unordered_set< T0 > & xs,
                                                    const std::unordered_set< T1 > & ys);
template < typename T0, typename T1 >
std::set< std::pair< T0, T1 > > operator*(const std::set< T0 > & xs,
                                          const std::set< T1 > & ys);

//-----------------------------------------------------------------------------
// Prototypes of powerset
//-----------------------------------------------------------------------------
template < typename T0, typename T1 >
T0 powset_(const T1 & X);

template < typename T >
std::set< std::set< T > > powset(const std::set< T > & X);

template < typename T >
std::unordered_set< std::unordered_set< T > > powset(const std::unordered_set< T > & X);

//-----------------------------------------------------------------------------
// Prototypes of operator<<
//-----------------------------------------------------------------------------
template < typename T0, typename T1 >
std::ostream & operator<<(std::ostream & cout, const std::pair< T0, T1 > & x);

template < typename T >
std::ostream & operator<<(std::ostream & cout, const std::vector< T > & x);

template < typename T >
std::ostream & operator<<(std::ostream & cout, const std::list< T > & x);

template < typename T >
std::ostream & operator<<(std::ostream & cout,
                          const std::unordered_set< T > & x);

template < typename S, typename T >
std::ostream & operator<<(std::ostream & cout,
                          const std::unordered_map< S, T > & x);

template < typename T >
std::ostream & operator<<(std::ostream & cout, const std::set< T > & x);

//=============================================================================
// Implementations
//=============================================================================

//-----------------------------------------------------------------------------
// Implementation of std::to_string extensions
//-----------------------------------------------------------------------------
namespace std
{
  inline
  std::string to_string(char c)
  {
    return {c};
  }
  
  inline
  std::string to_string(const std::string & x)
  {
    return x;
  }
  
  template <typename S, typename T>
  std::string to_string(const std::pair< S, T > & x)
  {
    return std::string("(") +
    to_string(x.first) + ", " + to_string(x.second) + ")";
  }

  // template < typename T >
  // std::string container_to_string_(const T & x, 
  //                                  const std::string & begin, 
  //                                  const std::string & end);

  template < typename T >
  std::string to_string(const std::vector< T > & x)
  {
    std::string ret = "[";
    std::string dir = "";
    for(int i = 0; i < x.size(); i++)
    {
      ret += (dir + to_string(x[i])); dir = ", ";
    }
    ret += ']';
    return ret;
  }

  template < typename T >
  std::string to_string(const std::list< T > & x)
  {
    std::list<T> temp = x;
    std::string ret = "[";
    std::string dir = "";
    while(temp.size() > 0)
    {
      T val = temp.front();
      ret += (dir + to_string(val)); dir = ", ";
      temp.pop_front();
    }
    ret += ']';
    return ret;
  }

  template < typename T >
  std::string to_string(const std::unordered_set< T > & x)
  {
    std::string ret = "{";
    std::string dir = "";
    
    for (auto& it : x)
    {
      ret += (dir + to_string(it)); dir = ", ";
    }
    ret += '}';
    return ret;
  }

  template < typename S, typename T >
  std::string to_string(const std::unordered_map< S, T > & x)
  {
    std::string ret = "{";
    std::string dir = "";
    
    for (auto it : x)
    {
      ret += (dir + (to_string(it.first) + ":" + to_string(it.second))); dir = ", ";
    }
    ret += '}';
    return ret;
  }

  template <typename T >
  std::string to_string(const std::set< T > & x)
  {
    std::string ret = "{";
    std::string dir = "";
    
    for (auto& it : x)
    {
      ret += (dir + to_string(it)); dir = ", ";
    }
    ret += '}';
    return ret;
  }
}

//-----------------------------------------------------------------------------
// Implementations of extensions to std::hash
//-----------------------------------------------------------------------------
namespace std
{
  template < typename S, typename T >
  struct hash< std::pair< S, T > >
  {
    size_t operator()(const std::pair< S, T > & x) const
    {
      std::hash< std::string > hasher;
      return hasher(std::to_string(x));
    }
  };

  template < typename T >
  struct hash< std::vector< T > >
  {
    size_t operator()(const std::vector< T > & x) const
    {
      std::hash< std::string > hasher;
      return hasher(std::to_string(x));
    }
  };
  
  template < typename T >
  struct hash< std::list< T > >
  {
    size_t operator()(const std::list< T > & x) const
    {
      std::hash< std::string > hasher;
      return hasher(std::to_string(x));
    }
  };

  template < typename T >
  struct hash< std::unordered_set< T > >
  {
    size_t operator()(const std::list< T > & x) const
    {
      std::hash< std::string > hasher;
      return hasher(std::to_string(x));
    }
  };

  // template < typename S, typename T, typename H >
  // struct hash< std::unordered_map< S, T, H > >
  // {};

  template < typename S >
  struct hash< std::set< S > >
  {
    size_t operator()(const std::set< S > & x) const
    {
      std::hash< std::string > hasher;
      return hasher(std::to_string(x));
    }
  };
}

//-----------------------------------------------------------------------------
// Implementation of memberships
//-----------------------------------------------------------------------------
template < typename S, typename T >
bool is_member(const S & e, const T & X)
{
  return X.find(e) != X.end();
}

template < typename S, typename T >
bool has(const S & X, const T & e)
{
    return X.find(e) != X.end();
}

//-----------------------------------------------------------------------------
// Implementations of set difference
//-----------------------------------------------------------------------------
template < typename T0, typename T1 >
void set_difference_(T0 & X, const T1 & Y)
{}

template < typename T >
const std::unordered_set< T > & operator-=(std::unordered_set< T > & X,
                                           const std::unordered_set< T > & Y)
{}

template < typename T >
std::unordered_set< T > operator-(const std::unordered_set< T > & X,
                                  const std::unordered_set< T > & Y)
{}

template < typename T >
const std::set< T > & operator-=(std::set< T > & X, const std::set< T > & Y)
{}

template < typename T >
std::set< T > operator-(const std::set< T > & X, const std::set< T > & Y)
{}

//-----------------------------------------------------------------------------
// Implementations of set union
//-----------------------------------------------------------------------------
template < typename T >
void set_union(T & x, const T & y)
{}

template < typename T >
std::set< T > & operator|=(std::set< T > & x, const std::set< T > & y)
{}

template < typename T >
std::set< T > operator|(const std::set< T > & x, const std::set< T > & y)
{}

template < typename T >
std::unordered_set< T > & operator|=(std::unordered_set< T > & x,
                                     const std::unordered_set< T > & y)
{}

template < typename T >
std::unordered_set< T > operator|(const std::unordered_set< T > & x,
                                  const std::unordered_set< T > & y)
{}

//-----------------------------------------------------------------------------
// Implementations of set intersection
//-----------------------------------------------------------------------------
template < typename T >
void set_intersection_(T & xs, const T & ys)
{}

template < typename T >
std::set< T > & operator&=(std::set< T > & xs, const std::set< T > & ys)
{}

template < typename T >
std::set< T > operator&(std::set< T > & x, const std::set< T > & y)
{}

template < typename T >
std::unordered_set< T > operator&=(std::unordered_set< T > & xs,
                                   const std::unordered_set< T > & ys)
{}

template < typename T >
std::unordered_set< T > operator&(std::unordered_set< T > & x,
                                  const std::unordered_set< T > & y)
{}


//------------------------------------------------------------------------------
// Implementations of cross product
//------------------------------------------------------------------------------
template < typename T0, typename T1, typename T2 >
void crossprod_(T0 & ret, const T1 & xs, const T2 & ys)
{
  // return std::string("INCOMPLETE");
}

template < typename T0, typename T1 >
std::set< std::pair< T0, T1 > > crossprod(const std::set< T0 > & xs,
                                          const std::set< T1 > & ys)
{
  return std::string("INCOMPLETE");
}

template < typename T0, typename T1 >
std::unordered_set< std::pair< T0, T1 > > crossprod(const std::unordered_set< T0 > & xs,
                                                    const std::unordered_set< T1 > & ys)
{
  return std::string("INCOMPLETE");
}

template < typename T0, typename T1 >
std::set< std::pair< T0, T1 > > operator*(const std::set< T0 > & xs,
                                          const std::set< T1 > & ys)
{
  return std::string("INCOMPLETE");
}

//-----------------------------------------------------------------------------
// Implementations of powerset
//-----------------------------------------------------------------------------
  template < typename T0, typename T1 >
  T0 powset_(const T1 & X)
  {
    return std::string("INCOMPLETE");
  }

  template < typename T >
  std::set< std::set< T > > powset(const std::set< T > & X)
  {
    return std::string("INCOMPLETE");
  }

  template < typename T >
  std::unordered_set< std::unordered_set< T > > powset(const std::unordered_set< T > & X)
  {
    return std::string("INCOMPLETE");
    
  }

//-----------------------------------------------------------------------------
// Implementations of operator<<
//-----------------------------------------------------------------------------
template < typename T0, typename T1 >
std::ostream & operator<<(std::ostream & cout, const std::pair< T0, T1 > & x)
{
  cout << std::to_string(x);
  return cout;
}

template < typename T >
std::ostream & operator<<(std::ostream & cout, const std::vector< T > & x)
{
  cout << std::to_string(x);
  return cout;
}

template < typename T >
std::ostream & operator<<(std::ostream & cout, const std::list< T > & x)
{
  cout << std::to_string(x);
  return cout;
}

template < typename T >
std::ostream & operator<<(std::ostream & cout,
                          const std::unordered_set< T > & x)
{
  cout << std::to_string(x);
  return cout;
}

template < typename S, typename T >
std::ostream & operator<<(std::ostream & cout,
                          const std::unordered_map< S, T > & x)
{
  cout << std::to_string(x);
  return cout;
}

template < typename T >
std::ostream & operator<<(std::ostream & cout, const std::set< T > & x)
{
  cout << std::to_string(x);
  return cout;
}

#endif