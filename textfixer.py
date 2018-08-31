file1 = open('genres.txt', 'r')
for line in file1.readlines():
    s = ' '
    print (s.join(line.split()[2:]))
