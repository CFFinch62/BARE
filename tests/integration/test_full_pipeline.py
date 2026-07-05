"""Integration tests — full-pipeline execution of complete BARE programs.

Tests the spec §10 example programs and additional multi-feature programs
end-to-end (source text → lexer → parser → interpreter → output).
"""

import pytest


class TestSpecExamples:
    """Test all example programs from the BARE spec §10."""

    def test_fizzbuzz(self, run):
        source = """
n = 1
while n <= 20
    if n % 15 == 0
        print "FizzBuzz"
    else
        if n % 3 == 0
            print "Fizz"
        else
            if n % 5 == 0
                print "Buzz"
            else
                print n
            end
        end
    end
    n = n + 1
end
"""
        expected = [
            "1", "2", "Fizz", "4", "Buzz",
            "Fizz", "7", "8", "Fizz", "Buzz",
            "11", "Fizz", "13", "14", "FizzBuzz",
            "16", "17", "Fizz", "19", "Buzz",
        ]
        assert run(source) == expected

    def test_factorial(self, run):
        source = """
sub factorial(n)
    if n <= 1
        return 1
    else
        return n * factorial(n - 1)
    end
end

print factorial(5)
"""
        assert run(source) == ["120"]

    def test_lists(self, run):
        source = """
scores = [88, 92, 75]
append(scores, 100)

total = 0
i = 0
while i < len(scores)
    total = total + scores[i]
    i = i + 1
end

print "Average: " + str(total / len(scores))
"""
        assert run(source) == ["Average: 88.75"]


class TestMultiFeaturePrograms:
    """Test programs that exercise multiple language features together."""

    def test_bubble_sort(self, run):
        source = """
nums = [5, 3, 1, 4, 2]
n = len(nums)
i = 0
while i < n
    j = 0
    while j < n - 1 - i
        if nums[j] > nums[j + 1]
            temp = nums[j]
            nums[j] = nums[j + 1]
            nums[j + 1] = temp
        end
        j = j + 1
    end
    i = i + 1
end
print nums
"""
        assert run(source) == ["[1, 2, 3, 4, 5]"]

    def test_fibonacci(self, run):
        source = """
sub fib(n)
    if n <= 0
        return 0
    end
    if n == 1
        return 1
    end
    a = 0
    b = 1
    i = 2
    while i <= n
        temp = b
        b = a + b
        a = temp
        i = i + 1
    end
    return b
end

print fib(10)
"""
        assert run(source) == ["55"]

    def test_string_building(self, run):
        source = """
result = ""
i = 1
while i <= 5
    result = result + str(i)
    if i < 5
        result = result + ", "
    end
    i = i + 1
end
print result
"""
        assert run(source) == ["1, 2, 3, 4, 5"]

    def test_nested_sub_calls(self, run):
        source = """
sub square(n)
    return n * n
end

sub sum_of_squares(a, b)
    return square(a) + square(b)
end

print sum_of_squares(3, 4)
"""
        assert run(source) == ["25"]

    def test_list_operations(self, run):
        source = """
sub sum_list(items)
    total = 0
    i = 0
    while i < len(items)
        total = total + items[i]
        i = i + 1
    end
    return total
end

data = [10, 20, 30, 40]
print "Sum: " + str(sum_list(data))
print "Count: " + str(len(data))
"""
        assert run(source) == ["Sum: 100", "Count: 4"]

    def test_input_with_conversion(self, run):
        source = """
name = input("Name: ")
age_str = input("Age: ")
age = num(age_str)
print "Hello " + name + ", you are " + str(age) + " years old."
"""
        result = run(source, input_values=["Alice", "30"])
        assert result == ["Hello Alice, you are 30 years old."]
