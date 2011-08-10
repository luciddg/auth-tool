import re

def check(password):
  results = []
  if len(password) < 7: 
    results.append('Password must be at least 8 characters')
  if not re.search('\d+', password):
    results.append('Password must contain at least one numeral')
  if not re.search('[a-z]',password) or not re.search('[A-Z]',password):
    results.append('Password must contain both uppercase and lowercase letters')
  if not re.search('.[!,@,#,$,%,^,&,*,?,_,~,-,(,)]',password):
    results.append('Password must contain at least one symbol')
  return results
