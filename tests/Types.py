from typing import TypedDict

# Schema for the function deep_nested_test() #
members_list_dto_0 = TypedDict("members_list_dto_0", {
   "id" : int,
   "name" : str,
   "roles" : list[str],
})

teams_sublist_0_list_dto_0 = TypedDict("teams_sublist_0_list_dto_0", {
   "id" : int,
   "name" : str,
   "members" : list[members_list_dto_0],
})

departments_list_dto_0 = TypedDict("departments_list_dto_0", {
   "name" : str,
   "teams" : list[list[teams_sublist_0_list_dto_0]],
})

deepNestedTest_dto = TypedDict("deepNestedTest_dto", {
   "departments" : list[departments_list_dto_0],
})

