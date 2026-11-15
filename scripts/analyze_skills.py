# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["numpy==2.3.4", "scipy==1.16.3", "scikit-learn==1.7.2", "matplotlib==3.10.7", "wordcloud==1.9.4", "networkx==3.5"]
# ///
"""Reproducible lexical analysis of checksum-pinned skills. No model APIs or weights."""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import json
from importlib.metadata import version
import platform
from pathlib import Path
import re
import sys
import urllib.request
import warnings

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261115
BOILERPLATE = {'skill', 'skills', 'claude', 'agent', 'agents', 'markdown', 'frontmatter',
 'metadata', 'version', 'allowed', 'tools', 'read', 'file', 'files', 'path', 'directory',
 'invoke', 'invocation', 'trigger', 'triggers', 'description', 'name', 'md', 'github',
 'https', 'com', 'output', 'input', 'user', 'use', 'using', 'used'}


def clean_text(source):
    """Retain prose and examples, drop frontmatter/code/URLs and markup, keep negation."""
    text = re.sub(r'\A---\s*\n.*?\n---\s*\n', '', source, flags=re.S)
    text = re.sub(r'```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~', '', text, flags=re.S)
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+|<!--[\s\S]*?-->', '', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    lines = []
    for line in html.unescape(text).splitlines():
        line = re.sub(r'^\s*(?:#+|[-*+]\s|\d+[.)]\s|>\s)', '', line)
        line = re.sub(r'[`*_~|]', ' ', line)
        line = re.sub(r'\s+', ' ', line).strip()
        if len(re.findall(r'\b[a-zA-Z]+\b', line)) >= 4:
            lines.append(line)
    return '\n'.join(lines)


def tokens(text):
    return re.findall(r"(?u)\b[^\W\d_]+(?:['’][^\W\d_]+)?\b", text.lower())


def shingles(text, size=5):
    result = set()
    for line in text.splitlines():
        words = tokens(line)
        result.update(' '.join(words[i:i + size]) for i in range(max(0, len(words)-size+1)))
    return result


def fetch_entry(entry, cache):
    target = cache / (entry['source_sha256'] + '.txt')
    try:
        if target.exists():
            body = target.read_bytes()
        else:
            url = entry['source_url'].replace('https://github.com/', 'https://raw.githubusercontent.com/', 1).replace('/blob/', '/', 1)
            request = urllib.request.Request(url, headers={'User-Agent': 'awesome-anti-slop-analysis'})
            with urllib.request.urlopen(request, timeout=40) as response:
                body = response.read()
        actual = hashlib.sha256(body).hexdigest()
        if actual != entry['source_sha256']:
            raise ValueError(f'checksum mismatch: expected {entry["source_sha256"]}, got {actual}')
        text = body.decode('utf-8-sig')
        cleaned = clean_text(text)
        if len(tokens(cleaned)) < 25:
            raise ValueError('fewer than 25 retained word tokens')
        target.write_bytes(body)
        return {'entry': entry, 'raw': text, 'clean': cleaned}, None
    except Exception as error:
        return None, {'id': entry['id'], 'reason': str(error)}


def bootstrap_lines(text, rng, fraction=.8):
    lines = text.splitlines()
    # Subsample without replacement: these are perturbation bands, not population CIs.
    count = max(1, round(len(lines)*fraction))
    selected = sorted(rng.choice(len(lines), size=count, replace=False))
    return '\n'.join(lines[i] for i in selected)


def sparse_set_matrix(sets):
    from scipy.sparse import csr_matrix
    vocab = {v: i for i, v in enumerate(sorted(set().union(*sets)))}
    rows, cols = [], []
    for i, values in enumerate(sets):
        for value in values:
            rows.append(i); cols.append(vocab[value])
    return csr_matrix(([1.] * len(rows), (rows, cols)), shape=(len(sets),len(vocab)))


def similarity_jaccard(sets):
    import numpy as np
    matrix = sparse_set_matrix(sets)
    intersection = (matrix @ matrix.T).toarray()
    sizes = np.array([len(x) for x in sets])
    union = sizes[:,None] + sizes[None,:] - intersection
    return np.divide(intersection, union, out=np.zeros_like(intersection), where=union>0)


def neighbors(matrix, k=5):
    import numpy as np
    matrix = matrix.copy()
    np.fill_diagonal(matrix, -np.inf)
    return np.argsort(-matrix, axis=1, kind='stable')[:, :k]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=60)
    args = parser.parse_args()
    if args.repeats < 2: parser.error('--repeats must be at least 2')
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform
    from scipy.stats import spearmanr
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    from sklearn.decomposition import NMF, TruncatedSVD
    from sklearn.cluster import AgglomerativeClustering, KMeans
    from sklearn.metrics import silhouette_score, adjusted_rand_score
    from sklearn.manifold import MDS, trustworthiness
    from sklearn.metrics.pairwise import cosine_similarity
    from wordcloud import WordCloud
    import networkx as nx
    # Isolated graph nodes intentionally create many singleton labels. sklearn's
    # classification warning is irrelevant to these partition-agreement checks.
    warnings.filterwarnings('ignore', message='The number of unique classes is greater than 50%.*',
                            category=UserWarning, module=r'sklearn.metrics.cluster._supervised')

    entries = json.loads((ROOT/'catalog.json').read_text())['entries']
    eligible = sorted([e for e in entries if e['kind']=='skill' and e.get('repo')], key=lambda e:e['id'].lower())
    cache = ROOT/'.cache/skill-analysis'; cache.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        loaded = list(pool.map(lambda e:fetch_entry(e, cache), eligible))
    corpus = [d for d, error in loaded if d]
    errors = [error for d, error in loaded if error]
    if len(corpus) < 10: raise SystemExit('Too few verified skills: '+json.dumps(errors))
    n = len(corpus); texts = [d['clean'] for d in corpus]
    rawtexts = [d['raw'] for d in corpus]
    stop = sorted((set(ENGLISH_STOP_WORDS) - {'no','not','never','without'}) | BOILERPLATE)
    word = TfidfVectorizer(stop_words=stop, ngram_range=(1,2), sublinear_tf=True,
                          min_df=2, max_df=.9, max_features=20000, strip_accents='unicode')
    X = word.fit_transform(texts)
    char = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), min_df=2, max_features=40000, sublinear_tf=True)
    C = char.fit_transform(texts)
    W = cosine_similarity(X); H = cosine_similarity(C)
    svd = TruncatedSVD(n_components=min(24,n-2,X.shape[1]-1), random_state=SEED)
    Z = svd.fit_transform(X)
    L = np.clip(cosine_similarity(Z), -1, 1)
    S = .7*W + .3*H
    rawvec = TfidfVectorizer(stop_words=sorted(set(ENGLISH_STOP_WORDS)-{'no','not','never','without'}), ngram_range=(1,2), sublinear_tf=True, min_df=2, max_features=20000)
    R = cosine_similarity(rawvec.fit_transform(rawtexts))
    fivegrams = [shingles(t) for t in texts]
    J = similarity_jaccard(fivegrams)
    distance = np.clip(1-S,0,2); np.fill_diagonal(distance,0)
    trials=[]
    for k in range(2,min(13,n-1)):
        labels=AgglomerativeClustering(n_clusters=k, metric='precomputed', linkage='average').fit_predict(distance)
        trials.append({'k':k,'silhouette':float(silhouette_score(distance, labels, metric='precomputed'))})
    chosen=max(trials,key=lambda x:x['silhouette'])['k']
    labels=AgglomerativeClustering(n_clusters=chosen,metric='precomputed',linkage='average').fit_predict(distance)
    nb=neighbors(S)
    # Mutual neighbors reduce generic hubs; the threshold is an exploratory choice.
    same_repo=np.array([[a['entry']['repo']==b['entry']['repo'] for b in corpus] for a in corpus])
    def cross_neighbors(sim):
        masked=sim.copy();masked[same_repo]=-1
        return neighbors(masked)
    def neighbor_graph(sim, k=5, threshold=.15, cross=False):
        masked=sim.copy()
        if cross:masked[same_repo]=-1
        near=neighbors(masked,k)
        graph=nx.Graph();graph.add_nodes_from(range(n))
        for i in range(n):
            for j in near[i]:
                if i<int(j) and i in near[j] and masked[i,j]>=threshold:
                    graph.add_edge(i,int(j),weight=float(sim[i,j]))
        return graph
    graph=neighbor_graph(S)
    def community_labels(g, seed):
        communities=nx.community.louvain_communities(g,weight='weight',seed=seed)
        communities=sorted(communities,key=lambda c:(-len(c),min(c)))
        values=np.zeros(n,dtype=int)
        for c,members in enumerate(communities):values[list(members)]=c
        return values,communities
    graph_labels,graph_communities=community_labels(graph,SEED)
    cross_graph=neighbor_graph(S,cross=True)
    cross_labels,cross_communities=community_labels(cross_graph,SEED)
    cross_nb=cross_neighbors(S)
    cross_counts=np.zeros((n,n));cross_aris=[]
    bridge_scores=nx.betweenness_centrality(graph,weight=None)
    graph_runs=[community_labels(graph,SEED+i)[0] for i in range(20)]
    graph_seed_ari=[adjusted_rand_score(graph_runs[i],graph_runs[j]) for i in range(20) for j in range(i)]
    graph_boot_ari=[]
    rng=np.random.default_rng(SEED)
    counts=np.zeros((n,n)); coassign=np.zeros((n,n)); similarities=[]; aris=[]
    for rep in range(args.repeats):
        sampled=[bootstrap_lines(t,rng) for t in texts]
        sw=cosine_similarity(word.transform(sampled)); sh=cosine_similarity(char.transform(sampled))
        sim=.7*sw+.3*sh; similarities.append(sim)
        for i,near in enumerate(neighbors(sim)): counts[i,near]+=1
        for i,near in enumerate(cross_neighbors(sim)):cross_counts[i,near]+=1
        dd=np.clip(1-sim,0,2);np.fill_diagonal(dd,0)
        ll=AgglomerativeClustering(n_clusters=chosen,metric='precomputed',linkage='average').fit_predict(dd)
        coassign+=(ll[:,None]==ll[None,:]);aris.append(adjusted_rand_score(labels,ll))
        gl,_=community_labels(neighbor_graph(sim),SEED)
        graph_boot_ari.append(adjusted_rand_score(graph_labels,gl))
        cl,_=community_labels(neighbor_graph(sim,cross=True),SEED)
        cross_aris.append(adjusted_rand_score(cross_labels,cl))
    counts/=args.repeats;coassign/=args.repeats
    cross_counts/=args.repeats
    low,high=np.quantile(np.array(similarities),[.05,.95],axis=0)
    # Independent stochastic view: unit-normalized latent vectors, 20 k-means seeds.
    nz=Z/np.maximum(np.linalg.norm(Z,axis=1,keepdims=True),1e-12)
    km=[KMeans(n_clusters=chosen,n_init=10,random_state=SEED+i).fit_predict(nz) for i in range(20)]
    km_ari=[adjusted_rand_score(km[i],km[j]) for i in range(len(km)) for j in range(i)]
    topic_count=min(8,n-2)
    nmf=NMF(n_components=topic_count,init='nndsvda',random_state=SEED,max_iter=1500)
    topic_weights=nmf.fit_transform(X); topic_weights/=np.maximum(topic_weights.sum(axis=1,keepdims=True),1e-12)
    features=np.array(word.get_feature_names_out())
    topics=[]
    for i,component in enumerate(nmf.components_):
        terms=features[np.argsort(component)[::-1][:10]].tolist()
        topics.append({'id':i,'terms':terms,'label':' / '.join(terms[:3])})
    # Repository prevalence, one vote per repository, limits multi-skill publisher inflation.
    repo_terms=defaultdict(set)
    for d in corpus: repo_terms[d['entry']['repo']].update(set(tokens(d['clean']))-set(stop))
    prevalence=Counter(term for terms in repo_terms.values() for term in terms)
    phrase_sets=defaultdict(set)
    for d,grams in zip(corpus,fivegrams):
        for phrase in grams:phrase_sets[phrase].add(d['entry']['repo'])
    shared_phrases=[{'phrase':p,'repositories':len(rs)} for p,rs in phrase_sets.items() if len(rs)>=3]
    shared_phrases.sort(key=lambda p:(-p['repositories'],p['phrase']))
    # Extractive distillation: each paragraph is represented by existing TF-IDF features.
    # Select a compact coverage set, without judging quality or printing upstream prose.
    paragraphs=[]
    for i,text in enumerate(texts):
        for j,line in enumerate(text.splitlines()):
            if 12<=len(tokens(line))<=160: paragraphs.append((i,j,line))
    P=word.transform([p[2] for p in paragraphs])
    # Coverage is over document-normalized vocabulary weights; quotes stay in the local cache.
    repo_indices=defaultdict(list)
    for i,d in enumerate(corpus):repo_indices[d['entry']['repo']].append(i)
    repo_profiles=np.vstack([np.asarray(X[ix].mean(axis=0)).ravel() for ix in repo_indices.values()])
    df=(repo_profiles>0).sum(axis=0)
    target=repo_profiles.mean(axis=0)
    target[df<3]=0; target/=target.sum()
    present=P.sign().tocsr()
    covered=np.zeros(X.shape[1],dtype=bool);selected=[]
    costs=np.array([max(12,len(tokens(p[2])))**.65 for p in paragraphs])
    for step in range(min(20,len(paragraphs))):
        gains=present@(target*~covered)
        # Ratio discourages a giant paragraph winning solely by length.
        score=gains/costs
        for old in selected:score[old['paragraph_index']]=-1
        pick=int(np.argmax(score));covered[present[pick].indices]=True
        i,j,line=paragraphs[pick]
        selected.append({'paragraph_index':pick,'skill_id':corpus[i]['entry']['id'],
                         'retained_line':j+1,'line_sha256':hashlib.sha256(line.encode()).hexdigest(),
                         'word_count':len(tokens(line)),'vocabulary_coverage':float(target[covered].sum())})
    # Jaccard null: destroy sequence while preserving word counts for the strongest phrase-overlap pairs.
    pairs=sorted([(i,j) for i in range(n) for j in range(i)],key=lambda ij:J[ij],reverse=True)
    nulls=[]
    for i,j in pairs[:10]:
        base=fivegrams[i]; shuffled=[]; words=tokens(texts[j])
        for rep in range(100):
            ww=rng.permutation(words).tolist();gg={' '.join(ww[p:p+5]) for p in range(len(ww)-4)}
            shuffled.append(len(base&gg)/max(1,len(base|gg)))
        nulls.append({'a':i,'b':j,'observed':float(J[i,j]),'shuffled_p95':float(np.quantile(shuffled,.95))})
    near=[]
    for i in range(n):
        near.append([{'index':int(j),'similarity':float(S[i,j]),'word_cosine':float(W[i,j]),
          'character_cosine':float(H[i,j]),'latent_cosine':float(L[i,j]),'phrase_jaccard':float(J[i,j]),
          'top5_retention':float(counts[i,j]),'perturbation_p05':float(low[i,j]),'perturbation_p95':float(high[i,j]),
          'coassignment':float(coassign[i,j])} for j in nb[i]])
    projection=MDS(n_components=2,dissimilarity='precomputed',random_state=SEED,n_init=8,max_iter=1000,normalized_stress=True)
    coords=projection.fit_transform(distance)
    upper=np.triu_indices(n,1)
    method_matrices={'word':W,'character':H,'latent':L,'phrase':J,'raw':R,'combined':S}
    correlations={a:{b:float(spearmanr(A[upper],B[upper]).statistic) for b,B in method_matrices.items()} for a,A in method_matrices.items()}
    clusters=[]
    for c in sorted(set(labels)):
        members=np.flatnonzero(labels==c)
        centroid=np.asarray(X[members].mean(axis=0)).ravel()
        terms=features[np.argsort(centroid)[::-1][:8]].tolist()
        inside=coassign[np.ix_(members,members)]
        stability=float(inside[np.triu_indices(len(members),1)].mean()) if len(members)>1 else None
        clusters.append({'id':int(c),'members':members.tolist(),'terms':terms,'stability':stability})
    result={'schema_version':1,'seed':SEED,'catalog_sha256':hashlib.sha256((ROOT/'catalog.json').read_bytes()).hexdigest(),
      'run_metadata':{'python':platform.python_version(),'analysis_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'packages':{package:version(package) for package in ['numpy','scipy','scikit-learn','matplotlib','wordcloud','networkx']}},
      'scope':{'catalog_entries':len(entries),'eligible_skills':len(eligible),'verified_skills':n,'repositories':len(repo_terms),
        'excluded_kinds':dict(Counter(e['kind'] for e in entries if e not in eligible)), 'failed_sources':errors,
        'scope_note':'Pinned entry files only; referenced guides and examples are not recursively fetched. Non-Latin tokenization is exploratory.'},
      'methods':{'combined':'0.7 word unigram/bigram TF-IDF cosine + 0.3 character 3-5gram TF-IDF cosine',
        'stopwords':stop,'clustering':'Average-linkage agglomerative clustering; k=2..12 selected by cosine-distance silhouette',
        'repeats':args.repeats,'perturbation':'80% retained prose lines without replacement; fixed fitted vocabulary and IDF',
        'distillation':'Greedy coverage of repository-balanced TF-IDF vocabulary appearing in 3+ repositories, per paragraph word-count^0.65; extraction locator only, not a quality ranking',
        'projection':'Metric MDS of combined distance; 2D placement is approximate; inspect exact neighbor scores',
        'phrase_null':'100 token-order permutations per selected high-overlap pair; exploratory, no hypothesis-test claims',
        'scope_caveat':'Textual similarity does not establish agreement, truth, effectiveness or authorial provenance.'},
      'clustering_trials':trials,'chosen_k':chosen,'clusters':clusters,'topics':topics,
      'knn_graph':{'k':5,'minimum_similarity':.15,'edges':graph.number_of_edges(),
        'isolates':list(nx.isolates(graph)), 'communities':[sorted(c) for c in graph_communities],
        'seed_ari_median':float(np.median(graph_seed_ari)),
        'perturbation_ari_median':float(np.median(graph_boot_ari)),
        'perturbation_ari_p05':float(np.quantile(graph_boot_ari,.05)),
        'perturbation_ari_p95':float(np.quantile(graph_boot_ari,.95)),
        'links':[{'a':i,'b':j,'weight':a['weight']} for i,j,a in graph.edges(data=True)]},
      'cross_repository_graph':{'k':5,'minimum_similarity':.15,'edges':cross_graph.number_of_edges(),
        'isolates':list(nx.isolates(cross_graph)), 'communities':[sorted(c) for c in cross_communities],
        'perturbation_ari_median':float(np.median(cross_aris)),
        'links':[{'a':i,'b':j,'weight':a['weight']} for i,j,a in cross_graph.edges(data=True)]},
      'graph_sensitivity':[{'k':k,'threshold':threshold,'isolates':len(list(nx.isolates(g))),
        'connected_groups':sum(len(c)>1 for c in community_labels(g,SEED)[1]),'edges':g.number_of_edges()}
        for k in [3,5,8] for threshold in [.10,.15,.20] for g in [neighbor_graph(S,k,threshold,cross=True)]],
      'stability':{'bootstrap_ari_median':float(np.median(aris)),'bootstrap_ari_p05':float(np.quantile(aris,.05)),
        'bootstrap_ari_p95':float(np.quantile(aris,.95)),'kmeans_seed_ari_median':float(np.median(km_ari)),
        'kmeans_vs_agglomerative_ari_median':float(np.median([adjusted_rand_score(labels,k) for k in km]))},
      'projection':{'stress':float(projection.stress_),'trustworthiness_k5':float(trustworthiness(X.toarray(),coords,n_neighbors=5,metric='cosine'))},
      'method_correlations':correlations,'repository_term_prevalence':prevalence.most_common(80),'shared_phrases':shared_phrases[:50],
      'extractive_coverage':selected,'phrase_null':nulls,
      'skills':[{'id':d['entry']['id'],'title':d['entry']['title'],'repo':d['entry']['repo'],'category':d['entry']['category'],
        'source_url':d['entry']['source_url'],'source_sha256':d['entry']['source_sha256'],'raw_words':len(tokens(d['raw'])),
        'retained_words':len(tokens(d['clean'])),'cluster':int(labels[i]),'graph_group':int(graph_labels[i]),
        'graph_bridge_score':float(bridge_scores[i]),'coordinates':coords[i].tolist(),
        'topic_weights':topic_weights[i].tolist(),'neighbors':near[i],
        'cross_repository_neighbors':[{'index':int(j),'similarity':float(S[i,j]),'top5_retention':float(cross_counts[i,j])} for j in cross_nb[i]]} for i,d in enumerate(corpus)],
      'matrices':{k:np.round(v,6).tolist() for k,v in method_matrices.items()},
      'top_pairs':[{'a':i,'b':j,'combined':float(S[i,j]),'phrase_jaccard':float(J[i,j]),'raw':float(R[i,j])}
        for i,j in sorted([(i,j) for i in range(n) for j in range(i)],key=lambda ij:S[ij],reverse=True)[:30]]}
    out=ROOT/'analysis';out.mkdir(exist_ok=True)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'skills.csv').open('w',newline='') as handle:
        writer=csv.writer(handle)
        writer.writerow(['index','id','repository','graph_group','dominant_topic','retained_words','nearest_skill','similarity','top5_retention','source_url','source_sha256'])
        for i,s in enumerate(result['skills']):
            j=s['neighbors'][0]['index']
            writer.writerow([i+1,s['id'],s['repo'],s['graph_group']+1,topics[int(np.argmax(s['topic_weights']))]['label'],
                s['retained_words'],result['skills'][j]['id'],round(S[i,j],6),round(counts[i,j],4),s['source_url'],s['source_sha256']])
    with (out/'pairs.csv').open('w',newline='') as handle:
        writer=csv.writer(handle)
        writer.writerow(['skill_a','skill_b','combined','word','character','latent','phrase_jaccard','a_top5_contains_b_retention','b_top5_contains_a_retention'])
        for i in range(n):
            for j in range(i):writer.writerow([corpus[i]['entry']['id'],corpus[j]['entry']['id'],*[round(float(m[i,j]),6) for m in [S,W,H,L,J,counts,counts.T]]])
    # Static scientific figures, suitable for repository rendering and export.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'figure.facecolor':'#faf9f5','axes.facecolor':'#faf9f5','savefig.facecolor':'#faf9f5'})
    palette=plt.get_cmap('tab20')
    def graph_figure(g,groups,title,filename):
        fig,ax=plt.subplots(figsize=(13,9))
        for i,j in g.edges:
            ax.plot(coords[[i,j],0],coords[[i,j],1],color='#b6b9b5',alpha=.35,linewidth=.6,zorder=0)
        isolated=[]
        for c in sorted(set(groups)):
            ix=np.flatnonzero(groups==c)
            if len(ix)==1:
                isolated.extend(ix.tolist());continue
            ax.scatter(coords[ix,0],coords[ix,1],s=70,c=[palette(int(c))],edgecolors='white',linewidth=.8,label=f'Group {int(c)+1} ({len(ix)})')
        if isolated:ax.scatter(coords[isolated,0],coords[isolated,1],s=55,facecolors='none',edgecolors='#777',label=f'No mutual links ({len(isolated)})')
        for i,(xx,yy) in enumerate(coords):ax.annotate(str(i+1),(xx,yy),xytext=(4,4),textcoords='offset points',fontsize=7)
        ax.set(title=title,xlabel='MDS coordinate 1 (arbitrary orientation)',ylabel='MDS coordinate 2 (arbitrary orientation)')
        ax.legend(loc='upper left',bbox_to_anchor=(1,1),frameon=False)
        fig.text(.02,.015,'Numbers identify skills in results.json and the generated index. Nearness is textual, not a quality score.',fontsize=9)
        fig.tight_layout(rect=(0,.035,1,1));fig.savefig(out/filename,dpi=165);plt.close(fig)
    graph_figure(graph,graph_labels,f'{n} verified skills: lexical neighborhood map','neighborhood-map.png')
    graph_figure(cross_graph,cross_labels,'Neighbors across repositories: same-repository edges excluded','cross-repository-map.png')
    order=leaves_list(linkage(squareform(distance,checks=True),method='average'))
    fig,ax=plt.subplots(figsize=(13,11))
    image=ax.imshow(S[np.ix_(order,order)],vmin=0,vmax=1,cmap='YlGnBu')
    ax.set_xticks(range(n),[str(i+1) for i in order],rotation=90,fontsize=6)
    ax.set_yticks(range(n),[str(i+1) for i in order],fontsize=6)
    ax.set(title='Shared wording forms overlapping families',xlabel='Skill index, ordered by average linkage',ylabel='Skill index')
    fig.colorbar(image,ax=ax,label='Combined TF-IDF cosine similarity',shrink=.7)
    fig.tight_layout();fig.savefig(out/'similarity-heatmap.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(13,10),gridspec_kw={'height_ratios':[1,1]})
    cloud=WordCloud(width=1800,height=650,background_color='#faf9f5',colormap='viridis',random_state=SEED,max_words=65,collocations=False)
    axes[0].imshow(cloud.generate_from_frequencies(dict(prevalence.most_common(65))),interpolation='bilinear');axes[0].axis('off')
    axes[0].set_title('Shared vocabulary: one vote per repository',loc='left',fontsize=16)
    pp=prevalence.most_common(18)[::-1]
    axes[1].barh([a for a,b in pp],[b for a,b in pp],color='#236b63')
    axes[1].set(xlabel=f'Repositories containing the term (out of {len(repo_terms)})',xlim=(0,len(repo_terms)))
    axes[1].grid(axis='x',alpha=.15)
    fig.tight_layout();fig.savefig(out/'shared-vocabulary.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(13,9))
    im=ax.imshow(topic_weights[order],aspect='auto',cmap='YlGnBu',vmin=0,vmax=1)
    ax.set_xticks(range(topic_count),[t['label'] for t in topics],rotation=40,ha='right',fontsize=8)
    ax.set_yticks(range(n),[str(i+1) for i in order],fontsize=6)
    ax.set(title='Skills mix several lexical topics',ylabel='Skill index')
    fig.colorbar(im,ax=ax,label='Normalized NMF weight (not a probability)',shrink=.65)
    fig.tight_layout();fig.savefig(out/'topic-mixtures.png',dpi=165);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,4.5))
    axes[0].plot([t['k'] for t in trials],[t['silhouette'] for t in trials],marker='o',color='#236b63')
    axes[0].set(title='Group-count sensitivity',xlabel='Number of groups',ylabel='Silhouette score')
    axes[0].axvline(chosen,color='#aa5533',linestyle='--',alpha=.7)
    axes[1].hist(aris,bins=12,color='#236b63');axes[1].set(title='Hierarchical split under line removal',xlabel='Adjusted Rand agreement',ylabel='Perturbation runs')
    axes[2].plot(range(1,len(selected)+1),[s['vocabulary_coverage'] for s in selected],marker='o',color='#236b63')
    axes[2].set(title='Extractive vocabulary coverage',xlabel='Selected paragraphs',ylabel='Repeated vocabulary weight covered',ylim=(0,1))
    fig.tight_layout();fig.savefig(out/'stability-and-coverage.png',dpi=165);plt.close(fig)
    names=list(method_matrices)
    fig,ax=plt.subplots(figsize=(8,7))
    cc=np.array([[correlations[a][b] for b in names] for a in names])
    im=ax.imshow(cc,vmin=0,vmax=1,cmap='YlGnBu')
    for i in range(len(names)):
        for j in range(len(names)):ax.text(j,i,f'{cc[i,j]:.2f}',ha='center',va='center',color='white' if cc[i,j]>.65 else '#222')
    ax.set_xticks(range(len(names)),names,rotation=35,ha='right');ax.set_yticks(range(len(names)),names)
    ax.set_title('Similarity methods agree unevenly\nSpearman correlation over all skill pairs')
    fig.colorbar(im,ax=ax,shrink=.7);fig.tight_layout();fig.savefig(out/'method-correlations.png',dpi=155);plt.close(fig)
    fig,axes=plt.subplots(4,2,figsize=(14,12))
    for t,ax,component in zip(topics,axes.flat,nmf.components_):
        terms={str(features[i]):float(component[i]) for i in np.argsort(component)[-35:] if component[i]>0}
        cloud=WordCloud(width=950,height=350,background_color='#faf9f5',colormap='viridis',random_state=SEED+t['id'],max_words=25,collocations=False)
        ax.imshow(cloud.generate_from_frequencies(terms));ax.axis('off');ax.set_title(t['label'],loc='left',fontsize=11)
    fig.suptitle('Eight lexical topics: weighted phrases, not generated labels',fontsize=16)
    fig.tight_layout(rect=(0,0,1,.97));fig.savefig(out/'topic-wordclouds.png',dpi=155);plt.close(fig)
    print(json.dumps({k:result[k] for k in ['scope','chosen_k','stability','projection']},indent=2))
    print('Mutual kNN graph:',len(graph_communities),'communities;',graph.number_of_edges(),'edges;',len(list(nx.isolates(graph))),'isolates; perturbation ARI',round(float(np.median(graph_boot_ari)),3))
    print('Top pairs:')
    for p in result['top_pairs'][:8]:print(round(p['combined'],3),corpus[p['a']]['entry']['id'],corpus[p['b']]['entry']['id'])
    return 0

if __name__=='__main__':
    sys.exit(main())
