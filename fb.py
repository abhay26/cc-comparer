inp(12)


def inp(x):
	n = x
	dic = {}
	for i in range(1,n+1):
		if n%15==0:
			dic[i] = "FIZZBUZZ"
		elif n%3==0:
			dic[i] = "FIZZ"
		elif n%5==0:
			dic[i] = "BUZZ"
		else:
			dic[i] = i
	print dic

