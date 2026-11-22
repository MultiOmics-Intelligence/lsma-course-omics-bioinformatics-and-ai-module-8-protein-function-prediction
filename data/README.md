# Data

| File | What it is | Source and licence |
|---|---|---|
| `uniprot_kinase_KW-0418.tsv` | Reviewed human proteins with the UniProt keyword KW-0418 (Kinase), 100 to 1,000 residues, not fragments: 492 proteins. | UniProtKB/Swiss-Prot, release 2026_04, downloaded on 22 November 2026 from the UniProt REST API (URL below). |
| `uniprot_protease_KW-0645.tsv` | The same for KW-0645 (Protease): 465 proteins. | As above. |
| `uniprot_ion_channel_KW-0407.tsv` | The same for KW-0407 (Ion channel): 273 proteins. | As above. |
| `get-data.sh` | Downloads the three files again, with the exact queries. | |

Each file is tab-separated, with the columns `Entry` (accession), `Gene Names (primary)`, `Protein families`, `Keyword ID`, `Length` and `Sequence`.

The query for the kinases, as one URL (the other two change only the keyword):

```
https://rest.uniprot.org/uniprotkb/stream?query=keyword:KW-0418 AND reviewed:true AND organism_id:9606 AND fragment:false AND length:[100 TO 1000]&fields=accession,gene_primary,protein_families,keywordid,length,sequence&format=tsv
```

These are real, public reference sequences of human proteins, not data from any person. UniProt changes between releases, so a new download with `bash data/get-data.sh` may give slightly different counts. Use the snapshot here if you want your numbers to match the checks most closely.

UniProt data are available under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) licence. Cite: The UniProt Consortium (2025), UniProt: the Universal Protein Knowledgebase in 2025, Nucleic Acids Research 53: D609-D617.
