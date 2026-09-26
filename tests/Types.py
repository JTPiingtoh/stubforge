from typing import TypedDict

# Schema for the function deep_nested_test() #
memberslist_dto_0 = TypedDict("memberslist_dto_0", {
   "id" : int,
   "name" : str,
   "roles" : list[str],
})

teamslist_dto_0 = TypedDict("teamslist_dto_0", {
   "id" : int,
   "name" : str,
   "members" : list[memberslist_dto_0],
})

departmentslist_dto_0 = TypedDict("departmentslist_dto_0", {
   "name" : str,
   "teams" : list[None | list[teamslist_dto_0]],
})

deepNestedTest_dto = TypedDict("deepNestedTest_dto", {
   "departments" : list[departmentslist_dto_0],
})

