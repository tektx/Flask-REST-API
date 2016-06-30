__author__ = 'Tek'


def reverseVowels(strin):
    temp = list(strin)
    positions_and_vowels = [(index, char) for index, char in enumerate(temp) if char in 'aeiouAEIOU']
    positions, vowels = [x[0] for x in positions_and_vowels], [x[1] for x in positions_and_vowels]
    vowels.reverse()
    for index, char in zip(positions, vowels):
        temp[index] = char
    return ''.join(temp)


def main():
    print reverseVowels('aA')


main()
