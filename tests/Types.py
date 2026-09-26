from typing import TypedDict

# Schema for the function deep_nested_test() #
memberslist_dto = TypedDict("memberslist_dto", {
   "id" : int,
   "name" : str,
   "roles" : list[str],
})

teamslist_dto = TypedDict("teamslist_dto", {
   "id" : int,
   "name" : str,
   "members" : list[memberslist_dto],
})

departmentslist_dto = TypedDict("departmentslist_dto", {
   "name" : str,
   "teams" : list[list[teamslist_dto]],
})

deepNestedTest_dto = TypedDict("deepNestedTest_dto", {
   "departments" : list[departmentslist_dto],
})

