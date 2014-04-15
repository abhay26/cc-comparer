from bs4 import BeautifulSoup
import requests


def invalidUser(soup):
	#print (soup)
	rating_table = soup.find("table", attrs={"class": "rating-table"})
	#print (val)
	if rating_table == None:
		return 1
	return 0

def getData(user):
	error = None
	for i in range(0,10):
		try:
			ob = requests.get("http://www.codechef.com/users/"+user)
		except:
			continue
		else:
			break
	page_source = ob.content
	soup = BeautifulSoup(page_source)
	if invalidUser(soup):
		return {"error": "Invalid User %s" % (user)}
	stats = getStats(soup)
	ranks = getRanks(soup)
	contests = getContests(soup)
	# db = get_db()
	# for cont in contests:
	# 	cur = db.execute('select * from entries where contest=?',(cont, ))
	# 	entries = cur.fetchall()
	# 	entries = list(entries)
	# 	if len(entries) > 0:
	# 		continue
	# 	print (cont)
	# 	loadContestData(cont)
	if 'error' in stats or 'error' in ranks or 'error' in contests:
		return {"error": "Data error."}
	return {'link': "http://www.codechef.com/users/"+user,'id': user,'stats': stats, 'ranks': ranks, 'contests': contests}




def getRanks(soup):
	rating_table = soup.find("table", attrs={"class": "rating-table"})
	all_ranks = rating_table.findAll("hx")
	if not all_ranks:
		return {"error": "Unexpected error"}
	dic = {"long_global": 'NA', "long_country": 'NA', "short_global": 'NA', "short_country": 'NA'}
	if all_ranks[0].string == 'NA':
		if all_ranks[1].string == 'NA':
			pass
		else:
			dic['short_global'] = all_ranks[1].string
			dic['short_country'] = all_ranks[2].string
	else:
		dic['long_global'] = all_ranks[0].string
		dic['long_country'] = all_ranks[1].string
		if all_ranks[2].string == 'NA':
			pass
		else:
			dic['short_global'] = all_ranks[2].string
			dic['short_country'] = all_ranks[3].string
	return dic

def getContests(soup):
	data = soup.findAll("table", attrs={"cellspacing":"0", "border":"0"})[1]
	bold = data.findAll("b")[12:]
	contests = []
	for entry in bold:
		contests.append(entry.string)
	return contests

def getStats(soup):
	data = soup.find("table", attrs={"cellpadding": ""})
	items = data.findAll("tr")[1]
	item = items.findAll("td")
	if not item:
		return {"error": "Unexpected error"}
	return {"solved": int(item[0].string), "submitted": item[1].string, "ac": item[2].string, "wa": item[3].string, "ce": item[4].string, "re": item[5].string, "tle": item[6].string}


# def getDetails(user, contest):
#     ob = requests.get("http://www.codechef.com/rankings/"+contest)
#     page_source = ob.content
#     soup = BeautifulSoup(page_source)
#     div_prob = soup.find("div", attrs={"class": "prob"})
#     if not div_prob:
#         return {"error": "The page does not seem to be correct, check contest exists"}
#     all_users = div_prob.findAll("tr")
#     all_users = all_users[1:]
#     if not all_users:
#         return {"error": "Nobody took part in this contest."}
#     for one_user in all_users:
#         if '>' + user + '<' in str(one_user):
#             rank = one_user.find("b").string
#             score = one_user.findAll("td")[-1].string
#             return {"rank":rank, "score": score}
#     return {"error": "The user did not participate in this contest."}


def loadContestData(contest):
	for i in range(0,10):
		try:
			ob = requests.get("http://www.codechef.com/rankings/"+contest)
		except:
			continue
		else:
			break
	page_source = ob.content
	soup = BeautifulSoup(page_source)
	# db = get_db()
	div_prob = soup.find("div", attrs={"class": "prob"})
	if not div_prob:
		print "error1"
		return {"error": "The page does not seem to be correct, check contest exists"}
	all_users = div_prob.findAll("tr")
	all_users = all_users[1:]
	if not all_users:
		print "error2"
		return {"error": "Nobody took part in this contest."}
	ret = []
	for user in all_users:
		userid = user.find("a").string
		rank = int(user.find("b").string)
		score = float(user.findAll("td")[-1].string)
		#print (userid, rank, score)
		ret.append([str(contest), userid, rank, score])
		# db.execute('insert into entries (contest, user, rank, score) values (?, ?, ?, ?)', [str(contest), userid, rank, score])
	return ret
	# db.commit()
	# db.close()


# def getDetails(contest):
#     # print "http://www.codechef.com/rankings/"+contest
#     ob = requests.get("http://www.codechef.com/rankings/"+contest)
#     page_source = ob.content
#     soup = BeautifulSoup(page_source)
#     div_prob = soup.find("div", attrs={"class": "prob"})
#     if not div_prob:
#         return {"error": "The page does not seem to be correct, check contest exists"}
#     all_users = div_prob.findAll("tr")
#     all_users = all_users[1:]
#     if not all_users:
#         return {"error": "Nobody took part in this contest."}
#     # return {"users": all_users}
#     return all_users


def userRankScore(contest, user, db):
    # print "LOL"
    # db = get_db()
    t = (user, contest, )
    cur = db.execute("SELECT * FROM entries WHERE user=? AND contest=?",t).fetchall()[0]
    return {"rank": cur['rank'], "score": cur['score']}

def getAllRanksMulti(contests, user1, user2, db):

	allRanks1 = {}
	allRanks2 = {}
	for contest in contests:
		allRanks1[contest] = userRankScore(contest, user1, db)
		allRanks2[contest] = userRankScore(contest, user2, db)
	return {user1: allRanks1, user2: allRanks2}


def getAllRanks(contests, user, db):
	allRanks = {}
	for contest in contests:
		allRanks[contest] = userRankScore(contest, user, db)
	return allRanks


