# coding= utf-8

import os
import json
import base
import requests
from requests.auth import HTTPDigestAuth

my_dir_name = os.path.dirname(os.path.realpath(__file__))

def authentication():
    ocfg = base.config.conf['ombis']
    token = HTTPDigestAuth(ocfg['user'], ocfg['password'])
    return token


def get(url, auth=None, cache=None):
    if not auth:
        auth = authentication()

    if cache:
        try:
            with open('cache/{}.json'.format(cache)) as f:
                return json.load(f)
        except:
            pass

    querystring = {"json": ""}

    response = requests.request("GET", url, auth=auth, params=querystring)

    res = json.loads(response.text)
    if cache:
        with open('cache/{}.json'.format(cache), 'w') as f:
            json.dump(res, f, indent=4)

    return res


if __name__ == "__main__":

    from base.common.orm import init_orm
    import src.models.models as models

    orm = init_orm().orm()
    session = orm.session()

    res = get(
        f'http://{cfg.ombis_host}:{cfg.ombis_port}/rest/web/00000001/serviceanfrage/?filter=gt(LastUpdateTime,2020-07-25)&fields=ID,Kunde,DisplayName,CreationTime,LastUpdateTime,BelegkreisKode,Nummer,Name,Beschreibung,PrioritaetReihenfolge,Status,VerknuepfteDokumente,EinsatzGeplantBisDatum,EinsatzGeplantBisZeit&refs=ZugewiesenAn(fields=Code,UserID,Suchbegriff,Matchcode&refs=CreatedBy,LastUpdateBy)')
    for ombis_data in res['Data']:

        ticket = models.Ticket.retreive_by_ombis_id(session, ombis_data)

        if not ticket:
            # uklanjanje \0 karaktera iz svih polja, ispostavilo se da ima dosta takvih
            # ne validnih karaktera koji za posledicu daju da podatak ne moze da se ubaci
            # u JSONB polje

            o = json.dumps(ombis_data, ensure_ascii=False)
            o = o.replace("\\u0000", '')

            ticket = models.Ticket(json.loads(o))

            session.add(ticket)


    session.commit()
