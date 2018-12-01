import pandas as pd
from sklearn.neighbors import NearestNeighbors as NN

class UserPredict():
    def __init__(self, algorithm='brute'):
        self.Users = pd.DataFrame(columns=['online', 0, 1, 2, 3, 4, 5])
        self.clf = NN(algorithm=algorithm, metric='hamming')

    def get_nears(self, userIDs, n):
        bufer = [self.Users.loc[x] for x in userIDs]
        return self.Users.index[self.clf.kneighbors(bufer, n, return_distance=False)].values
    
	def get_near(self, userID, n):
		return self.Users.index[self.clf.kneighbors([self.Users.loc[userID]],
                                                    n+1, return_distance=False)].values[0][1:]
    
    def add_user(self, userID, data):
        self.Users.loc[userID] = data
        self.clf.fit(self.Users)
    
    def set_user(self, userID, column, value):
		try:
			self.Users.loc[userID][column] = value
		except Exception as e:
			self.Users.loc[userID] = [1, 0, 0, 0, 0, 0, 0]
			self.Users.loc[userID][column] = value
		self.clf.fit(self.Users)

    def add_users(self, userIDs, data):
        for i, every in enumerate(userIDs):
            self.Users.loc[every] = data[i]
        self.clf.fit(self.Users)
        
    def deonline(self, userIDs):
        for every in userIDs:
            self.Users.loc[every]['online'] = 0
    
        self.clf.fit(self.Users)
    
    def online(self, userIDs):
        for every in userIDs:
            self.Users.loc[every]['online'] = 1
            
        self.clf.fit(self.Users)
