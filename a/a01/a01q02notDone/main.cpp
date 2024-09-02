#include <iostream>
#include <vector>
#include <string>

std::ostream& operator<<(std::ostream& cout, const std::vector<int>& x)
{
    std::string dir = "";
    for(int i = 0; i < x.size(); ++i)
    {
        cout << dir << x[i]; dir = "|";
    }
    return cout;
}

std::vector<int> getValues()
{
    std::vector<int> ret;
    int input;
    std::cin >> input;
    while (input != -1)
    {
        ret.push_back(input);
        std::cin >> input;
    }
    return ret;
}

int partition(std::vector<int> &vec, int low, int high) {

    // Selecting last element as the pivot
    int pivot = vec[high];

    // Index of elemment just before the last element
    // It is used for swapping
    int i = (low - 1);

    for (int j = low; j <= high - 1; j++) {

        // If current element is smaller than or
        // equal to pivot
        if (vec[j] <= pivot) {
            i++;
            std::swap(vec[i], vec[j]);
        }
    }

    // Put pivot to its position
    std::swap(vec[i + 1], vec[high]);

    // Return the point of partition
    return (i + 1);
}

void quickSort(std::vector<int> &vec, int low, int high) {

    // Base case: This part will be executed till the starting
    // index low is lesser than the ending index high
    if (low < high) {

        // p is partitioning index, arr[p] is now at
        // right place
        int p = partition(vec, low, high);

        // Separately sort elements before and after the
        // partition index p
        quickSort(vec, low, p - 1);
        quickSort(vec, p + 1, high);
    }
}

std::vector<int> delta(std::vector<int> x)
{
    std::vector<int> ret;
    for(int i = 0; i < x.size()-1; ++i)
    {
        for(int j = i+1; j < x.size(); ++j)
        {
            ret.push_back(x[j] - x[i]);
        }
    }
    quickSort(ret, 0,ret.size()-1);
    return ret;
}

std::vector<int> solve(std::vector<int> x)
{

}

int main()
{
    std::vector<int> x;
    x = getValues();
    std::vector<int> d = delta(x);
    std::cout << x << ' ' << d << std::endl;
    return 0;
}