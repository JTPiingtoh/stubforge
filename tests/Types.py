from typing import TypedDict

freeChampionIdsForNewPlayers_0_dto = TypedDict("freeChampionIdsForNewPlayers_0_dto", {
   "evil_name" : str,
   "age" : int,
   "job" : str,
   "life" : str,
})

freeChampionIdsForNewPlayers_1_dto = TypedDict("freeChampionIdsForNewPlayers_1_dto", {
   "name" : str,
   "age" : int,
   "job" : str,
   "life" : str,
})

details_dto = TypedDict("details_dto", {
   "name" : str,
   "age" : int,
   "job" : str,
})

listOfDetails_2_dto = TypedDict("listOfDetails_2_dto", {
   "name" : str,
   "age" : int,
   "date" : details_dto,
})

test_dto = TypedDict("test_dto", {
   "freeChampionIdsForNewPlayers" : list[freeChampionIdsForNewPlayers_0_dto | freeChampionIdsForNewPlayers_1_dto | int],
   "maxNewPlayerLevel" : int,
   "foo" : str,
   "bar" : int,
   "details" : details_dto,
   "list_of_details" : list[details_dto | listOfDetails_2_dto],
   "list_of_any" : list[int | listOfDetails_2_dto | str],
})

