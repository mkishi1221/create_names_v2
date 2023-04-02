data = {
  "choices": [
    {
      "finish_reason": "length",
      "index": 0,
      "logprobs": None,
      "text": "\n\n-Black-on-black ware \n-Puebloan Native American ceramic artists \n-Northern New Mexico \n-Reduction-fired blackware \n-Kha'po Owingeh and P'ohwh\u00f3ge Owingeh pueblos \n-"
    }
  ],
  "created": 1680439577,
  "id": "cmpl-70rO5LHi4s1CMSDqduggOUqBM6Z0H",
  "model": "text-davinci-003",
  "object": "text_completion",
  "usage": {
    "completion_tokens": 60,
    "prompt_tokens": 186,
    "total_tokens": 246
  }
}

print(data["choices"][0]["text"])