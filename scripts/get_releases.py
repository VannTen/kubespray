import requests
import os
import time
from datetime import datetime, timezone
from pprint import pprint


query="""
query($repoWithReleases: [ID!]!, $repoWithTags: [ID!]!) {
  with_releases: nodes(ids: $repoWithReleases) {

    ... on Repository {
      nameWithOwner
      releases(first: 100) {
        nodes {
          tagName
          isPrerelease
          releaseAssets {
            totalCount
          }
        }
      }
    }
  }

  with_tags: nodes(ids: $repoWithTags) {

    ... on Repository {
      nameWithOwner
      refs(refPrefix: "refs/tags/", last: 100) {
        nodes {
          name
        }
      }
    }
  }
}
"""
variables = {
    "repoWithReleases": [
        "R_kgDOAr9FWA", # containerd
        "R_kgDOBQqEpg", # cni
        "R_kgDOA87D0g", # calicoctl
        "R_kgDOE0nmLg", # ciliumcli
        "R_kgDOBMdURA", # crictl
        "R_kgDOBAr5pg", # crio
        "R_kgDOAKtHtg", # etcd
        "R_kgDOAToIkg", # k8s
        "R_kgDOEvuRnQ", # nerdctl
        "R_kgDOAjP4QQ", # runc
        "R_kgDOHQ6J9w", # skopeo
        "R_kgDOApOQGQ", # yq
    ],
    "repoWithTags": [
        "R_kgDOB9IlXg", # gvisor
    ],
}

response = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': variables}, headers={
    "Authorization": f"Bearer {os.getenv('API_KEY')}",
    })
response.raise_for_status()


full_res = response.json()
#pprint (full_res)
data = full_res["data"]
pprint ({**{repo["nameWithOwner"]: [release["tagName"] for release in repo["releases"]["nodes"] if not release["isPrerelease"] and release["releaseAssets"]["totalCount"] > 2]
         for repo in data["with_releases"]},
        **{repo["nameWithOwner"]: [release["name"] for release in repo["refs"]["nodes"]]
         for repo in data["with_tags"]}})
if 'x-ratelimit-used' in response.headers._store:
        print("ratelimit status: used %s of %s. next reset in %s minutes" % (
            response.headers['X-RateLimit-Used'],
            response.headers['X-RateLimit-Limit'],
            datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"]) - time.time(), tz=timezone.utc).strftime("%M:%S")
        ))
