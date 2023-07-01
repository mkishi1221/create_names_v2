# import os
# import openai
# openai.api_key = os.getenv("OPENAI_API_KEY")

# completion = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "user", "content": "find 15 short words related to innovative business"}
#   ]
# )

# print(completion.choices[0].message.content)


list_1 = ["x"]

list_total = []
for index in range(len(list_1)):
  list_total.append(list_1[index])
print("+".join(list_total))


