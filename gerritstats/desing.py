# extract_stats should be a method in a GerritProject class
# then:
#in __main__ test:
# after get_projects()
for proj in gerrit.projects:
    proj.extract_stats(...)

# then created a sorted list and print data

# maybe in GerritProjects distinguish active and inactive projects

# Q. how to interact with the parent object but invoke inherited methods

# Q. how to refactor extract_stats()
