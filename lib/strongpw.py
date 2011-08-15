import re

def check(password,username=''):
  results = []
  if len(password) < 7: 
    results.append('Error: password must be at least 8 characters')
  if not re.search('\d+', password):
    results.append('Error: password must contain at least one numeral')
  if not re.search('[a-z]',password) or not re.search('[A-Z]',password):
    results.append('Error: password must contain both uppercase and lowercase letters')
  if not re.search('.[!,@,#,$,%,^,&,*,?,_,~,\-,(,)]', password):
    results.append('Error: password must contain at least one symbol')
  if username:
    print username
    if re.search(username,password,re.I):
      results.append('Error: password may not contain username')
  return results
