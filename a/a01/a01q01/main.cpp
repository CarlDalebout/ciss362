#include <iostream>
#include <stack>

std::stack<int> getStack(int x)
{
    std::stack<int> ret;
    while(x>0)
    {
        int temp = x % 10;
        // std::cout << "pushing " << temp << " to top\n";
        ret.push(temp);
        x/=10;
        // std::cout << x << "\n";
    }
    return ret;
}



int findMax(std::stack<int> x)
{
    for(int i = 0; i < x.size(); i++)
    {

    }
    return -999;
}

std::stack<int> pancake(std::stack<int> x)
{
    for(int i = 0; i < x.size(); i++)
    {
        
    }
    return x;
}

std::ostream& operator<<(std::ostream& cout, const std::stack<int>& x)
{
    std::stack<int> temp = x;
    while(!temp.empty())
    {
        cout << temp.top();
        temp.pop();
    }
    return cout;
}


int main()
{
    int input;
    std::cin >> input; // getting value from user
    std::stack<int> stack = getStack(input); // creating stack from the value the user gave
    std::cout << stack << std::endl;
    // pancake(stack);
    // std::cout << stack << std::endl;

    return 0;
}