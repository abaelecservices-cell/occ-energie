"""Croise les départs et mentions de TS sans créer de liaison électrique."""
import re
import unicodedata
from collections import defaultdict, deque

def normalized(text):
    return unicodedata.normalize('NFD',text or '').encode('ascii','ignore').decode().upper()

def targets(text, boards):
    result=[]
    for prefix,number,half in re.findall(r'\b(TGBT|TS)\s*(\d+)\s*([AB])?\b',normalized(text)):
        exact=prefix+number+half
        target=exact if exact in boards else prefix+number
        if target not in result:
            result.append(target)
    return result

def build(data):
    boards={b['id']:b for b in data['boards']}
    nodes={n['id']:n for n in data['nodes']}
    down,up=defaultdict(list),defaultdict(list)
    for edge in data['edges']:
        down[edge['a']].append(edge['b']);up[edge['b']].append(edge['a'])
    def linked(node,target):
        seen={node};queue=deque([node])
        while queue:
            current=queue.popleft()
            for child in down[current]:
                if child in seen:continue
                seen.add(child)
                if nodes[child].get('board')==target:return True
                if nodes[child]['t']!='cpl':queue.append(child)
        return False
    records=[];shared=defaultdict(list)
    for node in data['nodes']:
        if node['t']!='dep':continue
        name=node['label'];xl=node.get('xl') or {};board=node.get('board')
        candidates=targets(name+' '+xl.get('label',''),boards)
        if node.get('feeds') and node['feeds'] not in candidates:candidates.append(node['feeds'])
        links=[]
        for target in candidates:
            if target==board:continue
            state='modele_documente' if target in boards and linked(node['id'],target) else 'a_recouper' if target in boards else 'tableau_non_repertorie'
            links.append(dict(target=target,status=state,explicitFeed=node.get('feeds')==target))
        buses=[parent for parent in up[node['id']] if nodes[parent]['t']=='bus']
        row=dict(id=node['id'],board=board,label=name,case=node.get('case') or node.get('cell'),
            source=node.get('src'),xl=xl,buses=buses,links=links,confidence=node.get('conf'))
        records.append(row)
        for reference in set(re.findall(r'\b\d{1,2}(?:PM|KM|SM|M|P|H|T)\s*\d{1,3}\b',normalized(name+' '+xl.get('label','')))):
            shared[reference.replace(' ','')].append(dict(node=node['id'],board=board,label=name))
    duplicates=[dict(reference=key,occurrences=value) for key,value in shared.items() if len({r['board'] for r in value})>1]
    summary=dict(departures=len(records),boards=len(boards),tgbt=sum(b['kind']=='TGBT' for b in boards.values()),
        modeled=sum(x['status']=='modele_documente' for r in records for x in r['links']),
        toReview=sum(x['status']=='a_recouper' for r in records for x in r['links']),
        unknown=sum(x['status']=='tableau_non_repertorie' for r in records for x in r['links']),sharedReferences=len(duplicates))
    return dict(summary=summary,departures=records,sharedReferences=duplicates)
