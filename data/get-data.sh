#!/bin/bash
# Download the three UniProt sets again (reviewed human proteins, 100-1000 residues).
# The files in data/ are a snapshot from UniProt release 2026_04 (22 November 2026).
# A new download may differ slightly, because UniProt changes between releases.
# Run from the top folder of your copy:   bash data/get-data.sh
set -euo pipefail
FIELDS="accession,gene_primary,protein_families,keywordid,length,sequence"
get () {   # $1 keyword, $2 output file
  curl -sS -G "https://rest.uniprot.org/uniprotkb/stream" \
    --data-urlencode "query=keyword:$1 AND reviewed:true AND organism_id:9606 AND fragment:false AND length:[100 TO 1000]" \
    --data-urlencode "fields=$FIELDS" \
    --data-urlencode "format=tsv" -o "$2"
  echo "$2: $(($(wc -l < "$2") - 1)) proteins"
}
get KW-0418 data/uniprot_kinase_KW-0418.tsv
get KW-0645 data/uniprot_protease_KW-0645.tsv
get KW-0407 data/uniprot_ion_channel_KW-0407.tsv
