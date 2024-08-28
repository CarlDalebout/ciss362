#include <iostream>
#include <stack>

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

std::stack<int> getSubStack(std::stack<int>& x, int size)
{
    std::stack<int> ret;
    for(int i = 0; i < size; ++i)
    {
        ret.push(x.top());
        x.pop();
    }
    return ret;
}

std::stack<int> mergeStacks(std::stack<int> subStack, std::stack<int> remainder)
{
    std::stack<int> ret;
    subStack.pop();
    while(subStack.size() > 0)
    {
        ret.push(subStack.top());
        subStack.pop();
    }
    while(remainder.size() > 0)
    {
        ret.push(remainder.top());
        remainder.pop();
    }
    return ret;
}

int findMax(std::stack<int> x, int size)
{
    std::stack<int> temp = x;
    int max = 0;
    int maxIndex = 0;
    for(int i = 0; i < size; ++i)
    {
        if(max == temp.top())
        {
            maxIndex = i;
        }
        else if(max < temp.top())
        {
            max = temp.top();
            maxIndex = i;
            
        }
        temp.pop();
    }
    return maxIndex+1;
}

std::stack<int> pancake(std::stack<int> x)
{
    std::stack<int> remainder = x;
    std::stack<int> subStack;
    std::stack<int> completed;
    // completed.push(9);
    while(completed.size() != x.size())
    {
        int subStackSize = findMax(remainder, remainder.size());
        if(subStackSize == remainder.size())
        {
            subStack = getSubStack(remainder, subStackSize);
            completed.push(subStack.top());
            remainder = mergeStacks(subStack, remainder);
            continue;
        }
        subStack = getSubStack(remainder, subStackSize);
        std::cout << subStack << remainder << completed << std::endl;
        completed.push(subStack.top());
        remainder = mergeStacks(subStack, remainder);
        std::cout << remainder << completed << std::endl;
    }
    return x;
}

int main()
{
    int input;
    std::cin >> input; // getting value from user
    std::stack<int> stack = getStack(input); // creating stack from the value the user gave
    std::cout << stack << std::endl;
    stack = pancake(stack);
    // std::cout << stack << std::endl;

    return 0;
}