from searchtweets import ResultStream, gen_rule_payload, load_credentials

import requests

#LIBREBOR HANDLERS

#SANDBOX: Si True utiliza la sandbox de LIBREBOR para no consumir consultas (usar con ITERATE = False)
#ITERATE: Si True utiliza el método recursivo para obtener también empresas constituidas por la original

SANDBOX = True
ITERATE = False
MAX_ITERS = 10

def person_by_slug(slug, auth, sandbox=""):
    url = f"https://{sandbox}api.librebor.me/v2/person/by-slug/{slug}/"
    req = requests.get(url, auth=auth)
    req.raise_for_status()
    req = req.json()
    return req["person"]


def company_by_nif(nif, auth, sandbox=""):
    url = f"https://{sandbox}api.librebor.me/v2/company/by-nif/{nif}/"
    req = requests.get(url, auth=auth)
    req.raise_for_status()
    req = req.json()
    return req["company"]


def company_by_slug(slug, auth, sandbox=""):
    url = f"https://{sandbox}api.librebor.me/v2/company/by-slug/{slug}/"
    req = requests.get(url, auth=auth)
    req.raise_for_status()
    req = req.json()
    return req["company"]


def find_company_offshore(company):
    pass


def find_person_offshore(person):
    pass


def format_person_slug(name):
    lname = name.split('-')
    if len(lname) >= 3:
        return ' '.join(lname[2:10] + lname[0:2])
    else:
        return ' '.join(lname[1:10] + lname[0:1])


def librebor_find_data(
    mongo, search_with_nif, slug, auth,
    visited=set(), results=[], iterations=0 if ITERATE else 20
):
    if search_with_nif:
        company = company_by_nif(
            slug, auth, sandbox="sandbox-" if SANDBOX else ""
        )
    else:
        company = company_by_slug(
            slug, auth, sandbox="sandbox-" if SANDBOX else ""
        )

    visited.add(company['slug'])

    iterations += 1

    offshore = False #find_company_offshore(company["name"])

    output = {
        "type": "company",
        "name": company["name"],
        "slug": company["slug"],
        "panama_papers": offshore
    }

    if "province" in company:
        output.update({"province": company["province"]})
    if "nif" in company:
        output.update({"nif": company["nif"]})
    if "previous_name" in company:
        output.update({"other_names": company["previous_name"]})

    results.append(output)

    positions = company["active_positions"] + company["inactive_positions"]
    for position in positions:
        if position["type"] == "Company" and not visited.issuperset({position["slug_company"]}) and iterations < MAX_ITERS:
            visited, results, iterations = librebor_find_data(
                mongo, False, position["slug_company"],
                auth, visited, results, iterations
            )
        elif position["type"] == "Person" and not visited.issuperset({position["slug_person"]}):
            visited.add(position["slug_person"])
            #offshore = find_person_offshore(position["name_person"])
            electoral = mongo.get_party_by_name(format_person_slug(position["slug_person"]))
            if electoral != list([]):
                electoral = electoral[0]["partido"]
            else:
                electoral = None

            results.append({
                "type": "person",
                "name": position["name_person"],
                "slug": position["slug_person"],
                "role": position["role"],
                "company": company["name"],
                "panama_papers": offshore,
                "electoral_lists": electoral
            })

    return visited, results, iterations


def tw_auth(twitter_keys_yaml_path):
    return load_credentials(
        twitter_keys_yaml_path,
        yaml_key="search_tweets_premium",
        env_overwrite=False
    )


def tw_query(str_query, n_results, auth, from_date="2021-09-01"):
    rule = gen_rule_payload(str_query, from_date=from_date, results_per_call=n_results)
    rs = ResultStream(
        rule_payload=rule,
        max_results=n_results,
        max_pages=1,
        **auth
    )
    tweets = []
    for tweet in rs.stream():
        if tweet.tweet_type in ['retweet']:
            continue
        if len(tweets) >= 10:
            break
        html = requests.get(
            f"https://publish.twitter.com/oembed?url=https://twitter.com/web/status/{tweet['id']}"
        )
        tweets.append(html.json()['html'])
    return tweets
