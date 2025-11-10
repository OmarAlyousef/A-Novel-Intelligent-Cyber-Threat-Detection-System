#  Associated Data

# Link Dataset 
https://www.stratosphereips.org/datasets-iot23

# 🔍 Dataset Description
	•	File Used: CTU-IoT-Malware-Capture-*.csv
	•	Source: CTU University, Czech Republic – IoT Malware Capture Dataset (IoT-23)
	•	Rows: Typically over 1 million records per capture file
	•	Columns: Over 80 features extracted from network flows (numeric & categorical)

# 🎯 Purpose

Detect and classify malicious network flows in IoT traffic, including Botnet, DDoS, and other attack types.

# 💾 Notes
	•	Multi-class labels representing various IoT attack categories.
	•	Missing or infinite values handled during preprocessing.
	•	Data extracted from .pcap files using feature engineering scripts.


#  Associated Data

# Link Dataset
https://www.unb.ca/cic/datasets/ids-2017.html

# 🔍 Dataset Description
- **File Used:** CIC-IDS2017 : MachineLearningCSV.zip (CSV files extracted from network traffic flows)
- **Source:** Canadian Institute for Cybersecurity – University of New Brunswick (UNB)
- **Rows:** Over 2.2 million records across all combined files
- **Columns:** 79 columns (78 numeric features + 1 label column)

# 🎯 Purpose
Provide realistic and labeled data for testing and evaluating Intrusion Detection Systems (IDS), including both normal traffic and multiple modern attack scenarios such as Brute Force, DoS/DDoS, Heartbleed, Web Attacks, Infiltration, and Botnet.

#  Associated Data

# Link Dataset
https://research.unsw.edu.au/projects/unsw-nb15-dataset

# 🔍 Dataset Description
	•	File Used: UNSW-NB15_*.csv (e.g., UNSW-NB15_1.csv … UNSW-NB15_4.csv), and the official splits UNSW_NB15_training-set.csv / UNSW_NB15_testing-set.csv.  ￼
	•	Source: UNSW Canberra (Australian Centre for Cyber Security). Raw traffic (≈100 GB PCAP) was generated with IXIA PerfectStorm in the Cyber Range Lab and released on the official UNSW page.  ￼
	•	Rows: ~2,540,044 total records across the complete dataset.  ￼
	•	Columns: 49 network-traffic features extracted using Argus & Bro/Zeek, plus label fields (attack_cat, label).

# 💾 Notes
- Multi-class labels representing various attack categories alongside normal traffic
- Imbalanced dataset, with attack traffic comprising approximately 20% of the total
- Features extracted from `.pcap` files using the CICFlowMeter tool and converted to CSV
- Some files contain missing or infinite values that need to be handled during preprocessing
