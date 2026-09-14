from typing import TypedDict

# Schema for the funciton test() #
test_dto = TypedDict("test_dto", {
   "name" : str,
   "age" : int,
   "active" : bool,
   "score" : float,
})

