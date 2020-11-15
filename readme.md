#Movies Website Backend

##Important paths
1. ``/api/users/`` - GETS all users, POST creates (registers) a user,
updates a user as well
1. ``/api-auth/login`` - returns header token in the form `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
1. ``/api-auth/logout`` - logs out the token

## Tags
1. ``/api/tags`` - returns all tags (only GET requests).

##Filtering Elements
All of these paths are with ``/api/elements`` in front of 'em
1. ``?tags=tag1,tag2`` - means that it will show all elements with tag1 AND tag2
1. ``?tags=tag1,tag2&or=true`` - means that it will show all elements with tag1 OR tag2
1. ``?tags__name=tag1`` - same as ``?tags=tag1``, but doesnt allow for multiple entries
1. ``?user=2`` - filters by the userId, you can leave it empty for null results, i.e. ``?user=`` 
1. ``?title=name`` - filters by title name
1. ``?search=some string to search with`` - searches for occurrences in title 
AND description of the given string 
