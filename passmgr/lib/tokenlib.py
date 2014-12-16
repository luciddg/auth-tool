import os
import cPickle as pickle
import datetime
import mkpass

tokensFile = (os.path.dirname(os.path.realpath( __file__ )) + '/../.tokens.pck') 

def generate(uid):
  token = mkpass.GenPasswd2(17)
  now = datetime.datetime.utcnow()
  newTokenData = { 'timestamp' : now, 'token' : token, 'uid' : uid }
  try:
    with open(tokensFile, 'rb') as tokensPck:
      tokenData = pickle.load(tokensPck)
  except:
    tokenData = []
  tokenData.append(newTokenData)
  try:
    with open(tokensFile, 'wb') as tokensPck:
      pickle.dump(tokenData,tokensPck)
    return token
  except:
    return

def delete(token):
  with open(tokensFile, 'rb') as tokensPck:
    tokenData = pickle.load(tokensPck)
  if len(tokenData) > 0:
    tokenData[:] = [d for d in tokenData if d.get('token') != token]
  with open(tokensFile, 'wb') as tokensPck:
    pickle.dump(tokenData, tokensPck)

def verify(token):
  now = datetime.datetime.utcnow()
  try:
    with open(tokensFile, 'rb') as tokensPck:
      tokenData = pickle.load(tokensPck)
    if len(tokenData) > 0:
      for dict in tokenData:
        if dict['token'] == token:
          match = dict
    if match:
      if (now - match['timestamp']).seconds < 360:
        return match['uid']
      else:
        delete(match['token'])
        return
  except:
    return 
