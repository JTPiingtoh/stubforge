from typing import TypedDict

matchV4_dto = TypedDict("matchV4_dto", {
   "leagueId" : str,
   "queueType" : str,
   "tier" : str,
   "rank" : str,
   "puuid" : str,
   "leaguePoints" : int,
   "wins" : int,
   "losses" : int,
   "veteran" : bool,
   "inactive" : bool,
   "freshBlood" : bool,
   "hotStreak" : bool,
})

freeChampionIdsForNewPlayers_dto = TypedDict("freeChampionIdsForNewPlayers_dto", {
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

listOfDetails_dto = TypedDict("listOfDetails_dto", {
   "name" : str,
   "age" : int,
   "date" : details_dto,
})

test_dto = TypedDict("test_dto", {
   "freeChampionIds" : list[int],
   "freeChampionIdsForNewPlayers" : list[freeChampionIdsForNewPlayers_dto | int],
   "maxNewPlayerLevel" : int,
   "foo" : str,
   "bar" : int,
   "details" : details_dto,
   "list_of_details" : list[details_dto | listOfDetails_dto],
   "list_of_any" : list[int | str | listOfDetails_dto],
})

freeChampionIdsForNewPlayers_dto = TypedDict("freeChampionIdsForNewPlayers_dto", {
   "name" : str,
   "age" : int,
   "job" : str,
   "life" : str,
})

test2_dto = TypedDict("test2_dto", {
   "freeChampionIds" : list[int],
   "freeChampionIdsForNewPlayers" : list[freeChampionIdsForNewPlayers_dto | int],
})

