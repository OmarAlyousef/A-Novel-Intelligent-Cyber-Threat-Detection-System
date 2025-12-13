<html>

<head>
<meta http-equiv=Content-Type content="text/html; charset=utf-8">
<meta name=Generator content="Microsoft Word 15 (filtered)">
<style>
<!--
 /* Font Definitions */
 @font-face
	{font-family:"Cambria Math";
	panose-1:2 4 5 3 5 4 6 3 2 4;}
@font-face
	{font-family:Aptos;
	panose-1:2 11 0 4 2 2 2 2 2 4;}
 /* Style Definitions */
 p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin-top:0cm;
	margin-right:0cm;
	margin-bottom:8.0pt;
	margin-left:0cm;
	line-height:115%;
	font-size:12.0pt;
	font-family:"Aptos",sans-serif;}
.MsoChpDefault
	{font-family:"Aptos",sans-serif;}
.MsoPapDefault
	{margin-bottom:8.0pt;
	line-height:115%;}
@page WordSection1
	{size:612.0pt 792.0pt;
	margin:72.0pt 72.0pt 72.0pt 72.0pt;}
div.WordSection1
	{page:WordSection1;}
-->
</style>

</head>

<body lang=en-SA style='word-wrap:break-word'>

<div class=WordSection1>

<p class=MsoNormal>import sys, subprocess, os, json, numpy as np, pandas as pd,
matplotlib.pyplot as plt, seaborn as sns</p>

<p class=MsoNormal>from pathlib import Path</p>

<p class=MsoNormal>def _req(m, pip_name=None, ver=None):</p>

<p class=MsoNormal>    try:</p>

<p class=MsoNormal>        __import__(m)</p>

<p class=MsoNormal>    except Exception:</p>

<p class=MsoNormal>        pk = pip_name or m</p>

<p class=MsoNormal>        if ver: pk += f&quot;=={ver}&quot;</p>

<p class=MsoNormal>       
subprocess.check_call([sys.executable,&quot;-m&quot;,&quot;pip&quot;,&quot;install&quot;,&quot;-q&quot;,pk])</p>

<p class=MsoNormal>_req(&quot;catboost&quot;,&quot;catboost&quot;,&quot;1.2.7&quot;)</p>

<p class=MsoNormal>_req(&quot;web3&quot;,&quot;web3&quot;,&quot;6.20.1&quot;)</p>

<p class=MsoNormal>_req(&quot;solcx&quot;,&quot;py-solc-x&quot;,&quot;2.0.3&quot;)</p>

<p class=MsoNormal>from catboost import CatBoostClassifier</p>

<p class=MsoNormal>from sklearn.preprocessing import LabelEncoder,
OrdinalEncoder, StandardScaler</p>

<p class=MsoNormal>from sklearn.metrics import classification_report,
confusion_matrix, roc_curve, auc, precision_recall_curve,
average_precision_score</p>

<p class=MsoNormal>from sklearn.compose import ColumnTransformer</p>

<p class=MsoNormal>from sklearn.pipeline import Pipeline</p>

<p class=MsoNormal>from web3 import Web3</p>

<p class=MsoNormal>from solcx import install_solc, compile_standard</p>

<p class=MsoNormal>try:</p>

<p class=MsoNormal>    from google.colab import drive</p>

<p class=MsoNormal>    drive.mount(&quot;/content/drive&quot;)</p>

<p class=MsoNormal>    GBASE = &quot;/content/drive/MyDrive&quot;</p>

<p class=MsoNormal>except Exception:</p>

<p class=MsoNormal>    GBASE = str(Path.home())</p>

<p class=MsoNormal>BASE = f&quot;{GBASE}/ICRDS-blockchain&quot;</p>

<p class=MsoNormal>DATA_DIR = f&quot;{GBASE}/UNSW-NB15&quot;</p>

<p class=MsoNormal>OUT = f&quot;{BASE}/outputs&quot;</p>

<p class=MsoNormal>Path(OUT).mkdir(parents=True, exist_ok=True)</p>

<p class=MsoNormal>def _pick(p, kw):</p>

<p class=MsoNormal>    cands = [f for f in Path(p).glob(&quot;*.csv&quot;)]</p>

<p class=MsoNormal>    for f in cands:</p>

<p class=MsoNormal>        if kw in f.name.lower(): return str(f)</p>

<p class=MsoNormal>    return str(sorted(cands)[0])</p>

<p class=MsoNormal>TR = _pick(DATA_DIR, &quot;training&quot;)</p>

<p class=MsoNormal>TE = _pick(DATA_DIR, &quot;testing&quot;)</p>

<p class=MsoNormal>df_tr = pd.read_csv(TR)</p>

<p class=MsoNormal>df_te = pd.read_csv(TE)</p>

<p class=MsoNormal>tcol = None</p>

<p class=MsoNormal>for c in
[&quot;attack_cat&quot;,&quot;Attack_cat&quot;,&quot;ATTACK_CAT&quot;,&quot;label&quot;,&quot;Label&quot;]:</p>

<p class=MsoNormal>    if c in df_tr.columns: tcol = c; break</p>

<p class=MsoNormal>if tcol is None: raise RuntimeError(&quot;target not
found&quot;)</p>

<p class=MsoNormal>if tcol.lower()==&quot;attack_cat&quot;:</p>

<p class=MsoNormal>    df_tr[tcol] = df_tr[tcol].fillna(&quot;Normal&quot;)</p>

<p class=MsoNormal>    df_te[tcol] = df_te[tcol].fillna(&quot;Normal&quot;)</p>

<p class=MsoNormal>y_tr = df_tr[tcol].astype(str)</p>

<p class=MsoNormal>y_te = df_te[tcol].astype(str)</p>

<p class=MsoNormal>drop_cols =
set([tcol,&quot;label&quot;,&quot;Label&quot;,&quot;id&quot;,&quot;ID&quot;,&quot;id.1&quot;])</p>

<p class=MsoNormal>X_tr = df_tr.drop(columns=[c for c in drop_cols if c in
df_tr.columns], errors=&quot;ignore&quot;)</p>

<p class=MsoNormal>X_te = df_te.drop(columns=[c for c in drop_cols if c in
df_te.columns], errors=&quot;ignore&quot;)</p>

<p class=MsoNormal>cat_cols =
X_tr.select_dtypes(include=[&quot;object&quot;,&quot;category&quot;]).columns.tolist()</p>

<p class=MsoNormal>num_cols = X_tr.columns.difference(cat_cols).tolist()</p>

<p class=MsoNormal>oe =
OrdinalEncoder(handle_unknown=&quot;use_encoded_value&quot;, unknown_value=-1)</p>

<p class=MsoNormal>sc = StandardScaler()</p>

<p class=MsoNormal>ct = ColumnTransformer([(&quot;cat&quot;, oe, cat_cols),
(&quot;num&quot;, sc, num_cols)], remainder=&quot;drop&quot;)</p>

<p class=MsoNormal>le = LabelEncoder().fit(pd.concat([y_tr,y_te],
ignore_index=True))</p>

<p class=MsoNormal>y_tr_enc = le.transform(y_tr)</p>

<p class=MsoNormal>y_te_enc = le.transform(y_te)</p>

<p class=MsoNormal>X_tr_s = ct.fit_transform(X_tr)</p>

<p class=MsoNormal>X_te_s = ct.transform(X_te)</p>

<p class=MsoNormal>vc = pd.Series(y_tr_enc).value_counts()</p>

<p class=MsoNormal>mx = vc.max()</p>

<p class=MsoNormal>class_weights = [mx/(vc[i] if i in vc.index else 1) for i in
range(len(le.classes_))]</p>

<p class=MsoNormal>cb =
CatBoostClassifier(loss_function=&quot;MultiClass&quot;,
eval_metric=&quot;TotalF1:average=Macro&quot;, class_weights=class_weights,
iterations=1200, depth=8, learning_rate=0.06, l2_leaf_reg=8.0, random_seed=42,
verbose=0)</p>

<p class=MsoNormal>cb.fit(X_tr_s, y_tr_enc, eval_set=(X_te_s, y_te_enc),
use_best_model=True, verbose=0)</p>

<p class=MsoNormal>pred_te = cb.predict(X_te_s).ravel().astype(int)</p>

<p class=MsoNormal>proba_te = cb.predict_proba(X_te_s)</p>

<p class=MsoNormal>classes = list(le.classes_)</p>

<p class=MsoNormal>rep = classification_report(y_te_enc, pred_te,
output_dict=True, target_names=classes, zero_division=0)</p>

<p class=MsoNormal>df_rep = pd.DataFrame(rep).T</p>

<p class=MsoNormal>for c in
[&quot;precision&quot;,&quot;recall&quot;,&quot;f1-score&quot;]:</p>

<p class=MsoNormal>    df_rep[c] = (df_rep[c]*100).round(2)</p>

<p class=MsoNormal>df_rep[&quot;support&quot;] =
df_rep[&quot;support&quot;].astype(int)</p>

<p class=MsoNormal>df_rep.to_csv(f&quot;{OUT}/classification_report_percent.csv&quot;)</p>

<p class=MsoNormal>plt.figure(figsize=(11,6))</p>

<p class=MsoNormal>mask_ix = [i for i in df_rep.index if i not in
[&quot;accuracy&quot;,&quot;macro avg&quot;,&quot;weighted avg&quot;]]</p>

<p class=MsoNormal>sns.heatmap(df_rep.loc[mask_ix,
[&quot;precision&quot;,&quot;recall&quot;,&quot;f1-score&quot;]].astype(float),
annot=True, fmt=&quot;.2f&quot;, cmap=&quot;Blues&quot;, vmin=0, vmax=100,
cbar_kws={&quot;ticks&quot;:[0,20,40,60,80,100]})</p>

<p class=MsoNormal>plt.title(&quot;Classification Report (%)&quot;)</p>

<p class=MsoNormal>plt.tight_layout()</p>

<p class=MsoNormal>plt.savefig(f&quot;{OUT}/classification_report_percent.png&quot;,
dpi=200)</p>

<p class=MsoNormal>plt.close()</p>

<p class=MsoNormal>cm = confusion_matrix(y_te_enc, pred_te)</p>

<p class=MsoNormal>plt.figure(figsize=(8,6))</p>

<p class=MsoNormal>sns.heatmap(cm, annot=True, fmt=&quot;d&quot;,
cmap=&quot;Greens&quot;, xticklabels=classes, yticklabels=classes)</p>

<p class=MsoNormal>plt.title(&quot;Confusion Matrix&quot;)</p>

<p class=MsoNormal>plt.tight_layout()</p>

<p class=MsoNormal>plt.savefig(f&quot;{OUT}/confusion_matrix.png&quot;,
dpi=200)</p>

<p class=MsoNormal>plt.close()</p>

<p class=MsoNormal>plt.figure(figsize=(8,6))</p>

<p class=MsoNormal>for i, cls in enumerate(classes):</p>

<p class=MsoNormal>    fpr, tpr, _ = roc_curve((y_te_enc==i).astype(int),
proba_te[:,i])</p>

<p class=MsoNormal>    plt.plot(fpr, tpr, label=f&quot;{cls}
(AUC={auc(fpr,tpr):.02f})&quot;)</p>

<p class=MsoNormal>plt.plot([0,1],[0,1],&quot;--&quot;,color=&quot;gray&quot;)</p>

<p class=MsoNormal>plt.title(&quot;ROC Curves&quot;)</p>

<p class=MsoNormal>plt.xlabel(&quot;False Positive Rate&quot;);
plt.ylabel(&quot;True Positive Rate&quot;)</p>

<p class=MsoNormal>plt.legend(loc=&quot;lower right&quot;, ncols=2, fontsize=8)</p>

<p class=MsoNormal>plt.tight_layout()</p>

<p class=MsoNormal>plt.savefig(f&quot;{OUT}/roc_curve.png&quot;, dpi=200)</p>

<p class=MsoNormal>plt.close()</p>

<p class=MsoNormal>plt.figure(figsize=(8,6))</p>

<p class=MsoNormal>for i, cls in enumerate(classes):</p>

<p class=MsoNormal>    p, r, _ =
precision_recall_curve((y_te_enc==i).astype(int), proba_te[:,i])</p>

<p class=MsoNormal>    ap = average_precision_score((y_te_enc==i).astype(int),
proba_te[:,i])</p>

<p class=MsoNormal>    plt.plot(r, p, label=f&quot;{cls} (AP={ap:.02f})&quot;)</p>

<p class=MsoNormal>plt.title(&quot;Precision-Recall Curves&quot;)</p>

<p class=MsoNormal>plt.xlabel(&quot;Recall&quot;);
plt.ylabel(&quot;Precision&quot;)</p>

<p class=MsoNormal>plt.legend(loc=&quot;best&quot;, ncols=2, fontsize=8)</p>

<p class=MsoNormal>plt.tight_layout()</p>

<p class=MsoNormal>plt.savefig(f&quot;{OUT}/pr_curve.png&quot;, dpi=200)</p>

<p class=MsoNormal>plt.close()</p>

<p class=MsoNormal>payloads = []</p>

<p class=MsoNormal>sel_cols = [c for c in
[&quot;srcip&quot;,&quot;sport&quot;,&quot;dstip&quot;,&quot;dsport&quot;,&quot;proto&quot;,&quot;state&quot;,&quot;service&quot;]
if c in df_te.columns]</p>

<p class=MsoNormal>for i in range(len(pred_te)):</p>

<p class=MsoNormal>    vals = []</p>

<p class=MsoNormal>    for k in sel_cols:</p>

<p class=MsoNormal>        try:</p>

<p class=MsoNormal>           
vals.append(f&quot;{k}:{str(df_te.iloc[i][k])}&quot;)</p>

<p class=MsoNormal>        except Exception:</p>

<p class=MsoNormal>            pass</p>

<p class=MsoNormal>    conf = float(np.max(proba_te[i]))</p>

<p class=MsoNormal>    vals.append(f&quot;pred:{classes[pred_te[i]]}&quot;)</p>

<p class=MsoNormal>    vals.append(f&quot;conf:{conf:.6f}&quot;)</p>

<p class=MsoNormal>    payloads.append(&quot;|&quot;.join(vals))</p>

<p class=MsoNormal>hashes = [Web3.keccak(text=s).hex() for s in payloads]</p>

<p class=MsoNormal>open(f&quot;{OUT}/prediction_hashes.json&quot;,&quot;w&quot;,encoding=&quot;utf-8&quot;).write(json.dumps(hashes,
indent=2))</p>

<p class=MsoNormal>install_solc(&quot;0.8.7&quot;)</p>

<p class=MsoNormal>src = &quot;&quot;&quot;</p>

<p class=MsoNormal>// SPDX-License-Identifier: MIT</p>

<p class=MsoNormal>pragma solidity ^0.8.7;</p>

<p class=MsoNormal>contract ICRDSLog {</p>

<p class=MsoNormal>    event RecordAdded(bytes32 hash, uint256 timestamp);</p>

<p class=MsoNormal>    bytes32[] public records;</p>

<p class=MsoNormal>    function addRecords(bytes32[] calldata hs) external {</p>

<p class=MsoNormal>        for (uint i=0;i&lt;hs.length;i++){</p>

<p class=MsoNormal>            records.push(hs[i]);</p>

<p class=MsoNormal>            emit RecordAdded(hs[i], block.timestamp);</p>

<p class=MsoNormal>        }</p>

<p class=MsoNormal>    }</p>

<p class=MsoNormal>    function total() external view returns(uint256){ return
records.length; }</p>

<p class=MsoNormal>}</p>

<p class=MsoNormal>&quot;&quot;&quot;</p>

<p class=MsoNormal>compiled = compile_standard({</p>

<p class=MsoNormal>    &quot;language&quot;:&quot;Solidity&quot;,</p>

<p class=MsoNormal>   
&quot;sources&quot;:{&quot;ICRDSLog.sol&quot;:{&quot;content&quot;:src}},</p>

<p class=MsoNormal>   
&quot;settings&quot;:{&quot;outputSelection&quot;:{&quot;*&quot;:{&quot;*&quot;:[&quot;abi&quot;,&quot;evm.bytecode.object&quot;]}}}</p>

<p class=MsoNormal>}, solc_version=&quot;0.8.7&quot;)</p>

<p class=MsoNormal>abi =
compiled[&quot;contracts&quot;][&quot;ICRDSLog.sol&quot;][&quot;ICRDSLog&quot;][&quot;abi&quot;]</p>

<p class=MsoNormal>bytecode =
compiled[&quot;contracts&quot;][&quot;ICRDSLog.sol&quot;][&quot;ICRDSLog&quot;][&quot;evm&quot;][&quot;bytecode&quot;][&quot;object&quot;]</p>

<p class=MsoNormal>provider =
os.environ.get(&quot;WEB3_PROVIDER&quot;,&quot;http://127.0.0.1:8545&quot;)</p>

<p class=MsoNormal>w3 = Web3(Web3.HTTPProvider(provider,
request_kwargs={&quot;timeout&quot;:120}))</p>

<p class=MsoNormal>ok = False</p>

<p class=MsoNormal>addr = None</p>

<p class=MsoNormal>if w3.is_connected():</p>

<p class=MsoNormal>    accts = []</p>

<p class=MsoNormal>    try:</p>

<p class=MsoNormal>        accts = w3.eth.accounts</p>

<p class=MsoNormal>    except Exception:</p>

<p class=MsoNormal>        accts = []</p>

<p class=MsoNormal>    if len(accts)&gt;0:</p>

<p class=MsoNormal>        acct = accts[0]</p>

<p class=MsoNormal>        factory = w3.eth.contract(abi=abi,
bytecode=bytecode)</p>

<p class=MsoNormal>        tx =
factory.constructor().transact({&quot;from&quot;:acct,&quot;gas&quot;:3_000_000,&quot;gasPrice&quot;:w3.to_wei(&quot;1&quot;,&quot;gwei&quot;)})</p>

<p class=MsoNormal>        rc = w3.eth.wait_for_transaction_receipt(tx)</p>

<p class=MsoNormal>        addr = rc.contractAddress</p>

<p class=MsoNormal>        c = w3.eth.contract(address=addr, abi=abi)</p>

<p class=MsoNormal>        bsz = 200</p>

<p class=MsoNormal>        for i in range(0,len(hashes),bsz):</p>

<p class=MsoNormal>            part = [Web3.to_bytes(hexstr=h) for h in
hashes[i:i+bsz]]</p>

<p class=MsoNormal>            tx =
c.functions.addRecords(part).transact({&quot;from&quot;:acct,&quot;gas&quot;:3_000_000,&quot;gasPrice&quot;:w3.to_wei(&quot;1&quot;,&quot;gwei&quot;)})</p>

<p class=MsoNormal>            w3.eth.wait_for_transaction_receipt(tx)</p>

<p class=MsoNormal>        ok = True</p>

<p class=MsoNormal>if ok:</p>

<p class=MsoNormal>   
open(f&quot;{OUT}/chain_contract.json&quot;,&quot;w&quot;,encoding=&quot;utf-8&quot;).write(json.dumps({&quot;address&quot;:addr,&quot;abi&quot;:abi},indent=2))</p>

<p class=MsoNormal>   
open(f&quot;{OUT}/onchain_hashes.json&quot;,&quot;w&quot;,encoding=&quot;utf-8&quot;).write(json.dumps(hashes,indent=2))</p>

<p class=MsoNormal>else:</p>

<p class=MsoNormal>   
open(f&quot;{OUT}/pending_hashes.json&quot;,&quot;w&quot;,encoding=&quot;utf-8&quot;).write(json.dumps({&quot;provider&quot;:provider,&quot;hashes&quot;:hashes},indent=2))</p>

<p class=MsoNormal>summary = {</p>

<p class=MsoNormal>    &quot;data_dir&quot;: DATA_DIR,</p>

<p class=MsoNormal>    &quot;train_file&quot;: TR,</p>

<p class=MsoNormal>    &quot;test_file&quot;: TE,</p>

<p class=MsoNormal>    &quot;classes&quot;: classes,</p>

<p class=MsoNormal>    &quot;macro_avg&quot;: df_rep.loc[&quot;macro avg&quot;,
[&quot;precision&quot;,&quot;recall&quot;,&quot;f1-score&quot;]].to_dict(),</p>

<p class=MsoNormal>    &quot;weighted_avg&quot;: df_rep.loc[&quot;weighted
avg&quot;,
[&quot;precision&quot;,&quot;recall&quot;,&quot;f1-score&quot;]].to_dict(),</p>

<p class=MsoNormal>    &quot;accuracy&quot;:
float(rep.get(&quot;accuracy&quot;,0))*100.0,</p>

<p class=MsoNormal>    &quot;web3_connected&quot;: ok,</p>

<p class=MsoNormal>    &quot;contract_address&quot;: addr</p>

<p class=MsoNormal>}</p>

<p class=MsoNormal>open(f&quot;{OUT}/summary.txt&quot;,&quot;w&quot;,encoding=&quot;utf-8&quot;).write(json.dumps(summary,
indent=2))</p>

<p class=MsoNormal>html = f&quot;&quot;&quot;</p>

<p class=MsoNormal>&lt;!doctype html&gt;&lt;meta
charset=&quot;utf-8&quot;&gt;&lt;title&gt;UNSW-NB15 Report&lt;/title&gt;</p>

<p class=MsoNormal>&lt;h3&gt;UNSW-NB15 Evaluation&lt;/h3&gt;</p>

<p class=MsoNormal>&lt;p&gt;Outputs: {OUT}&lt;/p&gt;</p>

<p class=MsoNormal>&lt;img src=&quot;classification_report_percent.png&quot;
style=&quot;max-width:100%;&quot;&gt;&lt;br&gt;</p>

<p class=MsoNormal>&lt;img src=&quot;confusion_matrix.png&quot;
style=&quot;max-width:100%;&quot;&gt;&lt;br&gt;</p>

<p class=MsoNormal>&lt;img src=&quot;roc_curve.png&quot;
style=&quot;max-width:100%;&quot;&gt;&lt;br&gt;</p>

<p class=MsoNormal>&lt;img src=&quot;pr_curve.png&quot;
style=&quot;max-width:100%;&quot;&gt;&lt;br&gt;</p>

<p class=MsoNormal>&lt;p&gt;Web3 connected: {ok}&lt;/p&gt;</p>

<p class=MsoNormal>&lt;p&gt;Contract: {addr}&lt;/p&gt;</p>

<p class=MsoNormal>&quot;&quot;&quot;</p>

<p class=MsoNormal>open(f&quot;{OUT}/report.html&quot;,&quot;w&quot;,encoding=&quot;utf-8&quot;).write(html)</p>

<p class=MsoNormal>print(&quot;DONE:&quot;, OUT)</p>

</div>

</body>

</html>
