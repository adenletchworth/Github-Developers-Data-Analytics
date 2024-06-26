def total_repositories(db):
    collection = db.github_repos  
    pipeline = [
        { "$count": "total_repositories" }
    ]
    return list(collection.aggregate(pipeline))

def repositories_by_license(db):
    collection = db.github_repos
    pipeline = [
        { "$group": { "_id": "$license", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } }
    ]
    return list(collection.aggregate(pipeline))

def repositories_by_language(db):
    collection = db.github_repos
    pipeline = [
        { "$unwind": "$languages" },  
        { "$group": { "_id": "$languages", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } }
    ]
    return list(collection.aggregate(pipeline))

def language_pairs(db):
    collection = db.github_repos
    pipeline = [
        { "$match": { "languages": { "$exists": True, "$ne": [] } } },
        { "$unwind": "$languages" },
        { 
            "$lookup": {
                "from": "github_repos",
                "localField": "_id",
                "foreignField": "_id",
                "as": "repo_languages"
            }
        },
        { "$unwind": "$repo_languages" },
        { "$unwind": "$repo_languages.languages" },
        { 
            "$project": {
                "pair": {
                    "$cond": [
                        { "$ne": [ "$languages", "$repo_languages.languages" ] },
                        { "source": "$languages", "target": "$repo_languages.languages" },
                        None
                    ]
                }
            }
        },
        { "$match": { "pair": { "$ne": None } } },
        { 
            "$group": {
                "_id": "$pair",
                "count": { "$sum": 1 }
            }
        },
        { "$sort": { "count": -1 }},
        { "$limit": 500 }
    ]
    return list(collection.aggregate(pipeline))


def activity_metrics(db):
    collection = db.github_repos
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_forks": { "$sum": "$forks_count" },
                "total_stargazers": { "$sum": "$stargazers_count" },
                "total_watchers": { "$sum": "$watchers_count" }
            }
        }
    ]
    return list(collection.aggregate(pipeline))

def top_keywords_from_descriptions(db):
    collection = db.github_repos
    pipeline = [
        { "$unwind": "$keywords_from_description" },
        { "$group": { "_id": "$keywords_from_description", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": 10 }
    ]
    return list(collection.aggregate(pipeline))

def top_keywords_from_readmes(db):
    collection = db.github_repos
    pipeline = [
        { "$unwind": "$keywords_from_readme" },
        { "$match": { "keywords_from_readme": { "$regex": "^[A-Za-z]+$", "$options": "i" } } },
        { "$group": { "_id": "$keywords_from_readme", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": 150 }
    ]
    return list(collection.aggregate(pipeline))


def avg_statistics(db):
    collection = db.github_repos
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_repos": { "$sum": 1 },
                "avg_forks": { "$avg": "$forks_count" },
                "avg_stargazers": { "$avg": "$stargazers_count" },
                "avg_watchers": { "$avg": "$watchers_count" },
                "avg_issues": { "$avg": "$open_issues_count" } 
            }
        }
    ]
    return list(collection.aggregate(pipeline))

def stars_over_time(db):
    collection = db.github_repos
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": { "format": "%Y-%m-%d", "date": { "$dateFromString": { "dateString": "$created_at" } } }
                },
                "total_stars": { "$sum": "$stargazers_count" }
            }
        },
        { "$sort": { "_id": 1 } }
    ]
    return list(collection.aggregate(pipeline))


if __name__ == "__main__":
    # Connect to MongoDB
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client["Developer"]
    print("Average statistics:", avg_statistics(db))

