#!/usr/bin/env python
# Source: http://carsongee.com/log/github-org-stats/
# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org/>

from __future__ import print_function

import csv
import json

from github import Github


def get_org_stats():
    """
    Get stats on each contributor in an organization on github.
    """
    username = "tisto"
    password = "TOKEN"
    org = "plone"
    g = Github(username, password)
    contributors = dict()

    repos = g.get_organization(org).get_repos()
    print(f"{repos.totalCount} repos found")
    for repo in repos:
        print(f"fetching contributors for {repo.name}")
        # if repo.fork:
        #     print('skipping ' + repo.full_name)
        #     continue
        repo_contributors = repo.get_stats_contributors()
        if not repo_contributors:
            continue

        for contributor in repo_contributors:
            login = contributor.author.login
            cont_data = contributors.get(login, dict())
            for stat in ("total_commits", "additions", "deletions"):
                cont_data[stat] = cont_data.get(stat, 0)
            cont_data["repos"] = cont_data.get("repos", [])
            cont_data["repos"].append(repo.full_name)
            cont_data["total_commits"] += contributor.total

            for week in contributor.weeks:
                for key, ghkey in (("additions", "a"), ("deletions", "d")):
                    cont_data[key] += getattr(week, ghkey)
            contributors[login] = cont_data
    # Dump JSON
    with open("data.json", "w") as outfile:
        json.dump(contributors, outfile, indent=2)

    # Dump CSV
    user_list = []
    for user in contributors:
        additions = contributors[user]["additions"]
        deletions = contributors[user]["deletions"]
        user_list.append(
            (
                user,
                contributors[user]["total_commits"],
                additions,
                deletions,
                additions + deletions,
                len(contributors[user]["repos"]),
            )
        )
    with open("data.csv", "w") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            [
                "username",
                "commits",
                "additions",
                "deletions",
                "changes",
                "number of repos",
            ]
        )
        for row in user_list:
            csv_writer.writerow(row)


if __name__ == "__main__":
    get_org_stats()
