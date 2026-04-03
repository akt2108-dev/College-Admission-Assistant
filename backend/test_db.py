from db import execute_query

query = "SELECT COUNT(*) FROM cutoffs;"
result = execute_query(query)

print(result)